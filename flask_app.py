from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import OrderedDict
import requests
import json
import os
import math

app = Flask(__name__)


def read_from_file(file_name):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, 'data/%s.json' % file_name)

	with open(file_path) as data_file:
		data = json.load(data_file)
		return data


def write_to_file(file_name, data):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, 'data/%s.json' % file_name)

	with open(file_path, "w") as jsonFile:
		json.dump(data, jsonFile)


@app.route("/api/players")
def get_players():
	players = read_from_file('players')
	return jsonify(list(players.keys()))


@app.route("/api/rnd/<int:rnd>")
def get_round(rnd):

	if rnd >= 5:
		return get_later_round(rnd)

	rnd_str = "round%s" % rnd
	teams = read_from_file('teams')
	rounds = read_from_file('rounds')
	players = read_from_file('players')

	result = {}
	for region, team_list in teams.items():
		players_and_teams = get_players_and_teams(players, rnd_str, team_list)

		pairs = []

		for game in rounds.get(region).get(rnd_str):
			pairs.append(get_pair(game, players_and_teams))

		result[region] = pairs

	return jsonify(result)	


def get_later_round(rnd):
	rnd_str = "round%s" % rnd
	teams = read_from_file('teams')
	rounds = read_from_file('rounds')
	players = read_from_file('players')

	players_and_teams = {}
	for region, team_list in teams.items():
		players_and_teams = get_players_and_teams_by_team_id(players, rnd_str, team_list, players_and_teams)

	pairs = []

	for game in rounds.get(rnd_str):
		pairs.append(get_pair(game, players_and_teams))

	return jsonify(pairs)


def get_players_and_teams_by_team_id(players, rnd_str, team_list, players_and_teams):
	team_list = {int(k): v for k, v in team_list.items()}
	for key, v in players.items():
		value = v.get(rnd_str)
		for teamId in value:
			if team_list.get(teamId) is not None:
				t = team_list.get(teamId)
				players_and_teams[teamId] = {"team": t[0], "player": key, "seed": t[1], "team_id": teamId}
	return players_and_teams


def get_pair(game, players_and_teams):
	t1, t2 = None, None
	fav, spread, time_left = None, 0, None
	if game:
		if len(game) >= 6:
			fav = game[4]
			spread = game[5]
			if spread == '0':
				spread = 'EVEN'
			time_left = get_time_left(game)
		t1 = get_it(0, players_and_teams, game)
		t2 = get_it(1, players_and_teams, game)

	return {"teams": [t1, t2], "spread": spread, "fav": fav, "timeLeft": time_left}


def get_players_and_teams(players, rnd_str, team_list):
	team_list = {int(k): v for k, v in team_list.items()}
	players_and_teams = {}
	for key, v in players.items():
		value = v.get(rnd_str)
		for teamId in value:
			if team_list.get(teamId) is not None:
				t = team_list.get(teamId)
				players_and_teams[t[1]] = {"team": t[0], "player": key, "seed": t[1], "team_id": teamId}

	return players_and_teams


def set_late_round_winner(rnd, result, region):
	rnd_str = "round%s" % rnd
	teams = read_from_file('teams')
	players = read_from_file('players')
	rounds = read_from_file('rounds')

	players_and_teams = {}
	for team_list in teams.items():
		players_and_teams = get_players_and_teams_by_team_id(players, rnd_str, team_list, players_and_teams)

	team_id_1 = result[0].get("team_id")
	team_id_2 = result[1].get("team_id")
	found_game = None
	for game in rounds.get(rnd_str):
		if game[0] in (team_id_1, team_id_2) and game[1] in (team_id_1, team_id_2):
			found_game = game
			break

	winner, winner_id, fav, spread = get_winner(found_game, players_and_teams)

	update_tables(winner, rnd+1, region, winner_id)

	return {"winner": winner, "round": rnd + 1, "region": region, "winner_id": winner_id}


def set_winner(rnd, region, result):
	# I have the seed, rnd and region of the teams, that should give me the players
	if rnd >= 5:
		return set_late_round_winner(rnd, result, region)

	rnd_str = "round%s" % rnd
	teams = read_from_file('teams')
	players = read_from_file('players')
	rounds = read_from_file('rounds')

	team_list = teams.get(region)
	players_and_teams = get_players_and_teams(players, rnd_str, team_list)

	# find the game
	seed1 = result[0].get("seed")
	seed2 = result[1].get("seed")
	found_game = None
	for game in rounds.get(region).get(rnd_str):
		if game[0] in (seed1, seed2) and game[1] in (seed1, seed2):
			found_game = game
			break

	winner, seed_winner, fav, spread = get_winner(found_game, players_and_teams)

	update_tables(winner, rnd+1, region, seed_winner)

	return {"winner": winner, "round": rnd + 1, "region": region, "seed": seed_winner}


def get_winner(game, players_and_teams):
	winner, winner_id, fav, spread = None, None, None, None
	if game is not None:
		fav = game[4]
		spread = math.floor(float(game[5]))
		spread = int(spread)

		if game[2] >= game[3]:
			winner_id = game[0]
		else:
			winner_id = game[1]

		if players_and_teams[game[0]].get("team") == fav:
			if game[2] + spread >= game[3]:
				winner = players_and_teams[game[0]].get("player")
			else:
				winner = players_and_teams[game[1]].get("player")
		else:
			if game[3] + spread >= game[2]:
				winner = players_and_teams[game[1]].get("player")
			else:
				winner = players_and_teams[game[0]].get("player")

	return winner, winner_id, fav, spread


def get_time_left(game):
	time_left = 'Final'
	quarter, q_sup = None, None
	if len(game) == 7:
		entire_string = game[6]
		if entire_string in ['Final/OT', 'Final', 'Half', '0:00']:
			time_left = entire_string
		else:
			time_left, quarter = entire_string.split()
			q_sup = quarter[1:]
			quarter = quarter[0]

	return {"time": time_left, "quarter": quarter, "sup": q_sup}


def get_it(i, players_and_teams, game):
	t1 = None
	if game[i] is not None:
		if len(game) >= 6:
			team_score = game[i + 2]
		else:
			team_score = 0
		t1 = players_and_teams[game[i]]
		t1["score"] = team_score

	return t1


@app.route("/")
def index():
	return render_template('index.html')


def remove_game(game_id):
	games = read_from_file("games")
	if game_id in games["games"]:
		del games["games"][game_id]
	write_to_file("games", games)

	return jsonify(games)


def game_started(game_time):
	now = datetime.utcnow()
	date = game_time["date"]
	start_time = game_time["starttime"]
	g_str = '%s 2017  %sM' % (date, start_time)
	g_time = datetime.strptime(g_str, '%b %d %Y %I:%M%p')
	g_utc = g_time + timedelta(hours=5)

	return now > g_utc


@app.route("/api/updatescore/v2")
def get_game_score_web():
	games = read_from_file("games")
	updating_games = []
	for game_id, game in games.get("games").items():
		if game_started(game):
			result, fav, spread, region, rnd, time_left = get_game_score(game_id)
			s1, score1 = result[0].get("seed"), result[0].get("score")
			s2, score2 = result[1].get("seed"), result[1].get("score")
			setscore(rnd, region, s1, score1, s2, score2, fav, spread, time_left)
			if 'Final' in time_left:
				remove_game(game_id)
				set_winner(rnd, region, result)
			else:
				updating_games.append(game_id)
	return jsonify(updating_games)


@app.route("/api/game/<game_id>")
def get_single_game(game_id):
	result, fav, spread, region, rnd, time_left = get_game_score(game_id)
	s1, score1 = result[0].get("seed"), result[0].get("score")
	s2, score2 = result[1].get("seed"), result[1].get("score")
	setscore(rnd, region, s1, score1, s2, score2, fav, spread, time_left)
	winner = set_winner(rnd, region, result)

	return jsonify(winner)


def get_game_score(game_id):
	req = 'http://www.espn.com/mens-college-basketball/game?gameId=%s' % game_id
	soup = getSoup(req)

	region, rnd = get_region_and_round(soup)

	result = [
		scrape_team(soup, 'team away'),
		scrape_team(soup, 'team home')
	]

	try:
		time_tag = soup.find("span", {"class": "game-time"})
		time_left = time_tag.text
		if time_left == 'Halftime':
			time_left = 'Half'
		elif time_left == '':
			time_left = "0:00"
		else:
			time_left = time_tag.text.replace(" - ", " ").replace(" Half", "")
	except:
		time_left = "0:00"

	try:
		line_div_tag = soup.find("div", {"class": "odds-details"})
		line_text = line_div_tag.findNext("li").text
		if 'EVEN' in line_text:
			fav = result[0].get("abbrev")
			line = "0"
		else:
			fav, line = line_div_tag.findNext("li").text.replace("Line: ", "").split()
	except:
		fav, line = None, None

	return result, fav, line, region, rnd, time_left


def get_region_and_round(soup):
	region_tag = soup.find("div", {"class": "game-details header"})
	reg = region_tag.text.replace("MEN'S BASKETBALL CHAMPIONSHIP - ", "")
	if "NATIONAL" in reg:
		region = None
		rnd = 6
	elif "FINAL" in reg:
		region = None
		rnd = 5
	elif "ELITE" in reg:
		region = reg.replace(" REGION - ELITE 8", "")
		rnd = 4
	elif "SWEET" in reg:
		region = reg.replace(" REGION - SWEET 16", "")
		rnd = 3
	else:
		reg = reg.replace(" ROUND", "").replace(" REGION -", "")
		region, rnd = reg.split()
		rnd = int(rnd[0])

	return region, rnd


def scrape_team(soup, team_class):
	team_tag = soup.find("div", {"class": team_class})
	rank = team_tag.find("span", {"class": "rank"}).text
	abbrev = team_tag.find("span", {"class": "abbrev"}).text
	try:
		score = int(team_tag.find("div", {"class": "score"}).text)
	except:
		score = 0
	return {"seed": int(rank), "score": score, "abbrev": abbrev}


def setscore(rnd, region, seed1, score1, seed2, score2, fav, spread, time_left):
	round_str = "round%s" % rnd
	rounds = read_from_file('rounds')
	matchup, slot = get_matchup_and_slot(rnd, seed1)
	while len(rounds[region][round_str][matchup]) < 7:
		rounds[region][round_str][matchup].append(None)

	rounds[region][round_str][matchup][slot+2] = score1
	matchup, slot = get_matchup_and_slot(rnd, seed2)
	rounds[region][round_str][matchup][slot+2] = score2
	rounds[region][round_str][matchup][4] = fav
	rounds[region][round_str][matchup][5] = spread
	rounds[region][round_str][matchup][6] = time_left

	write_to_file('rounds', rounds)
	return 'set em'


@app.route("/api/current_round")
def get_current_round():
	games = read_from_file("games")
	rounds = games.get("rounds")
	rounds = OrderedDict(sorted(rounds.items()))
	result = find_current_round(rounds)
	return jsonify(result)


def find_current_round(rounds):
	now = (datetime.utcnow() - timedelta(hours=5)).date()
	result = []
	r_rnd = 1

	for rnd, date in rounds.items():
		r_str = '%s 2017' % date
		r_date = datetime.strptime(r_str, '%b %d %Y').date()
		if now < r_date:
			break
		else:
			r_rnd = int(rnd)

	result.append(r_rnd)
	return result


@app.route("/api/update/<player_name>/<int:rnd>/<region>/<int:seed>")
def update_tables(player_name, rnd, region, seed):
	if rnd >= 5:
		update_player_file(player_name, rnd, seed)
	else:
		team_id, team = getTeamBySeed(region, seed)
		update_player_file(player_name, rnd, team_id)

	update_round_file(region, rnd, seed)

	return 'got em'


def update_round_file(region, rnd, seed):
	round_str = "round%s" % rnd
	rounds = read_from_file('rounds')

	if rnd >= 5:
		matchup, slot = get_late_round_matchup_and_slot(region, rnd)
		rounds[round_str][matchup][slot] = seed

	else:
		matchup, slot = get_matchup_and_slot(rnd, seed)
		rounds[region][round_str][matchup][slot] = seed

	write_to_file('rounds', rounds)


def get_late_round_matchup_and_slot(region, rnd):
	matchup, slot = None, None
	if rnd == 5:
		if region == 'EAST':
			matchup, slot = 0, 0
		elif region == 'MIDWEST':
			matchup, slot = 0, 1
		elif region == 'SOUTH':
			matchup, slot = 1, 1
		elif region == 'WEST':
			matchup, slot = 1, 0

	elif rnd == 6:
		if region in ['EAST', 'MIDWEST']:
			matchup, slot = 0, 0
		elif region in ['SOUTH', 'WEST']:
			matchup, slot = 0, 1

	return matchup, slot


def get_matchup_and_slot(rnd, seed):
	matchup, slot = None, None
	if rnd == 1:
		if seed == 1:
			matchup, slot = 0, 0
		elif seed == 16:
			matchup, slot = 0, 1
		elif seed == 8:
			matchup, slot = 1, 0
		elif seed == 9:
			matchup, slot = 1, 1
		elif seed == 5:
			matchup, slot = 2, 0
		elif seed == 12:
			matchup, slot = 2, 1
		elif seed == 4:
			matchup, slot = 3, 0
		elif seed == 13:
			matchup, slot = 3, 1
		elif seed == 6:
			matchup, slot = 4, 0
		elif seed == 11:
			matchup, slot = 4, 1
		elif seed == 3:
			matchup, slot = 5, 0
		elif seed == 14:
			matchup, slot = 5, 1
		elif seed == 7:
			matchup, slot = 6, 0
		elif seed == 10:
			matchup, slot = 6, 1
		elif seed == 2:
			matchup, slot = 7, 0
		elif seed == 15:
			matchup, slot = 7, 1

	if rnd == 2:
		if seed in [1, 16]:
			matchup, slot = 0, 0
		elif seed in [8, 9]:
			matchup, slot = 0, 1
		elif seed in [5, 12]:
			matchup, slot = 1, 0
		elif seed in [4, 13]:
			matchup, slot = 1, 1
		elif seed in [6, 11]:
			matchup, slot = 2, 0
		elif seed in [3, 14]:
			matchup, slot = 2, 1
		elif seed in [7, 10]:
			matchup, slot = 3, 0
		elif seed in [2, 15]:
			matchup, slot = 3, 1

	elif rnd == 3:
		if seed in [1, 16, 8, 9]:
			matchup, slot = 0, 0
		elif seed in [5, 12, 4, 13]:
			matchup, slot = 0, 1
		elif seed in [6, 11, 3, 14]:
			matchup, slot = 1, 0
		elif seed in [7, 10, 2, 15]:
			matchup, slot = 1, 1

	elif rnd == 4:
		if seed in [1, 16, 8, 9, 5, 12, 4, 13]:
			matchup, slot = 0, 0
		elif seed in [6, 11, 3, 14, 7, 10, 2, 15]:
			matchup, slot = 0, 1

	return matchup, slot


def update_player_file(player, rnd, team_id):
	round_str = "round%s" % rnd
	players = read_from_file('players')

	players[player][round_str].append(team_id)

	write_to_file('players', players)


def getTeamById(team_id):
	teams = read_from_file('teams')
	for region in teams.items():
		if team_id in region:
			return region.get(team_id)[0]


def getTeamBySeed(region, seed):
	teams = read_from_file('teams')
	teamList = teams.get(region)
	for id, curr_team in teamList.items():
		if curr_team[1] == seed:
			team_id = id
			team = curr_team
			break

	return int(team_id), team


def getSoup(url):
	html = requests.get(url)
	text = html.text
	soup = BeautifulSoup(text, "html.parser")
	return soup

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5050)


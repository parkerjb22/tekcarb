from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import requests
import json, os

app = Flask(__name__)


def readFromFile(fileName):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, 'data/%s.json' % fileName)

	with open(file_path) as data_file:
		data = json.load(data_file)
		return data


def writeToFile(fileName, data):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, 'data/%s.json' % fileName)

	with open(file_path, "w") as jsonFile:
		json.dump(data, jsonFile)


@app.route("/api/players")
def getPlayers():
	players = readFromFile('players')
	return jsonify(list(players.keys()))


@app.route("/api/rnd/<int:rnd>")
def getRound(rnd):
	rndStr = "round%s" % rnd
	teams = readFromFile('teams')
	rounds = readFromFile('rounds')
	players = readFromFile('players')
	result = {}
	for region, teamList in teams.items():
		teamList = {int(k): v for k, v in teamList.items()}
		pairs = []
		playersAndTeams = {}
		for key, v in players.items():
			value = v.get(rndStr)
			for teamId in value:
				if teamList.get(teamId) is not None:
					t = teamList.get(teamId)
					playersAndTeams[t[1]] = {"team": t[0], "player": key, "seed": t[1]}

		if (rnd == 5):
			pass
			# "round5": [
			# 	[1, 1, 55, 34, "KU", "-55"],
			# 	[1, 1, 55, 34, "UNC", "-55"]
			# ]


		else:
			for game in rounds.get(region).get(rndStr):
				t1, t2 = None, None
				fav, spread = None, 0
				if game:
					if len(game) == 6:
						fav = game[4]
						spread = game[5]
					t1 = getit(0, playersAndTeams, game)
					t2 = getit(1, playersAndTeams, game)

				pairs.append({"teams": [t1, t2], "spread": spread, "fav": fav})

			result[region] = pairs

	return jsonify(result)	


def getit(i, playersAndTeams, game):
	t1 = None
	if game[i] is not None:
		if len(game) == 6:
			team_score = game[i + 2]
		else:
			team_score = 0
		t1 = playersAndTeams[game[i]]
		t1["score"] = team_score

	return t1


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/api/addgame/<gameId>")
def add_game(gameId):
	games = readFromFile("games")
	if gameId not in games["games"]:
		games["games"].append(gameId)
	writeToFile("games", games)

	return jsonify(games)

@app.route("/api/removegame/<gameId>")
def remove_game(gameId):
	games = readFromFile("games")
	if gameId in games["games"]:
		games["games"].remove(gameId)
	writeToFile("games", games)

	return jsonify(games)


@app.route("/api/updatescore")
def get_game_score_web():
	games = readFromFile("games")
	for game in games.get("games"):
		result, fav, spread, region, rnd = get_game_score(game)
		setscore(rnd, region, result[0].get("seed"), result[0].get("score"), result[1].get("seed"), result[1].get("score"), fav, spread)

	return 'got em'


def get_game_score(game_id):
	req = 'http://www.espn.com/mens-college-basketball/game?gameId=%s' % game_id
	soup = getSoup(req)

	result = []

	regionTag = soup.find("div", {"class":"game-details header"})
	reg = regionTag.text.replace("MEN'S BASKETBALL CHAMPIONSHIP - ", "").replace(" ROUND", "").replace(" REGION -", "")
	region, rnd = reg.split()
	rnd = int(rnd[0])

	result.append(scrapeTeam(soup,'team away'))
	result.append(scrapeTeam(soup, 'team home'))

	try:
		lineDivTag = soup.find("div", {"class": "odds-details"})
		fav, line = lineDivTag.findNext("li").text.replace("Line: ", "").split()
	except:
		fav, line = None, None

	return result, fav, line, region, rnd


def scrapeTeam(soup, teamClass):
	teamTag = soup.find("div", {"class": teamClass})
	rank = teamTag.find("span", {"class": "rank"}).text
	try:
		score = int(teamTag.find("div", {"class": "score"}).text)
	except:
		score = 0
	return {"seed": int(rank), "score": score}


@app.route("/api/setscore/<int:rnd>/<region>/<int:seed1>/<int:score1>/<int:seed2>/<int:score2>/<fav>/<spread>")
def setscore(rnd, region, seed1, score1, seed2, score2, fav, spread):
	round_str = "round%s" % rnd
	rounds = readFromFile('rounds')
	matchup, slot = getMatchupAndSlot(rnd, seed1)
	while len(rounds[region][round_str][matchup]) < 6:
		rounds[region][round_str][matchup].append(None)

	rounds[region][round_str][matchup][slot+2] = score1
	matchup, slot = getMatchupAndSlot(rnd, seed2)
	rounds[region][round_str][matchup][slot+2] = score2
	rounds[region][round_str][matchup][4] = fav
	rounds[region][round_str][matchup][5] = spread

	writeToFile('rounds', rounds)
	return 'set em'

@app.route("/api/setgameid/<int:rnd>/<region>/<int:seed>/<int:game_id>")
def setgameid(rnd, region, seed, game_id):
	round_str = "round%s" % rnd
	rounds = readFromFile('rounds')

	matchup, slot = getMatchupAndSlot(rnd, seed)

	if len(rounds[region][round_str][matchup]) == 2:
		rounds[region][round_str][matchup].append(game_id)

	writeToFile('rounds', rounds)
	return 'set em'

@app.route("/api/update/<player_name>/<int:rnd>/<region>/<int:seed>")
def updateTables(player_name, rnd, region, seed):
	team_id, team = getTeamBySeed(region, seed)
	updatePlayerFile(player_name, rnd, team_id)
	updateRoundFile(region, rnd, seed)

	return 'got em'


def updateRoundFile(region, rnd, seed):
	round_str = "round%s" % rnd
	rounds = readFromFile('rounds')

	matchup, slot = getMatchupAndSlot(rnd, seed)

	rounds[region][round_str][matchup][slot] = seed
	writeToFile('rounds', rounds)

def getMatchupAndSlot(rnd, seed):
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

def updatePlayerFile(player, rnd, team_id):
	round_str = "round%s" % rnd
	players = readFromFile('players')

	players[player][round_str].append(team_id)

	writeToFile('players', players)


def getTeamBySeed(region, seed):
	teams = readFromFile('teams')
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


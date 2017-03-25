from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
from collections import OrderedDict
from lib.common import read_from_file, get_players_and_teams_by_team_id, get_pair, get_players_and_teams

app = Flask(__name__)


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


@app.route("/")
def index():
	return render_template('index.html')


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


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5050)


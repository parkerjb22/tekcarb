from flask import Flask, render_template, jsonify, abort
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

		for game in rounds.get(region).get(rndStr):
			t1, t2 = None, None
			if game:
				if game[0] is not None:
					t1 = playersAndTeams[game[0]]
				if game[1] is not None:
					t2 = playersAndTeams[game[1]]

			pairs.append({"teams": [t1, t2]})

		result[region] = pairs

	return jsonify(result)	


@app.route("/")
def index():
	return render_template('index.html')


@app.route("/api/update/<player_name>/<int:rnd>/<region>/<int:seed>")
def updateTables(player_name, rnd, region, seed):
	team_id, team = getTeamBySeed(region, seed)
	updatePlayerFile(player_name, rnd, team_id)
	updateRoundFile(region, rnd, seed)

	return 'got em'


def updateRoundFile(region, rnd, seed):
	round_str = "round%s" % rnd
	rounds = readFromFile('rounds')

	if (rnd == 2):
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

	rounds[region][round_str][matchup][slot] = seed
	writeToFile('rounds', rounds)

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


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5050)


from flask import Flask, render_template, jsonify
import json

app = Flask(__name__)

def readFromFile(fileName):
	with open('data/%s.json' % fileName) as data_file:
		data = json.load(data_file)
		return data

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
			if game:
				t1 = playersAndTeams[game[0]]
				t2 = playersAndTeams[game[1]]
				pairs.append({"teams": [t1, t2]})
			else:
				pairs.append({"teams": [None, None]})

		result[region] = pairs

	return jsonify(result)	

@app.route("/")
def index():
	 return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)


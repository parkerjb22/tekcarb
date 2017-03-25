import json
import os


def read_from_file(file_name):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, '../data/%s.json' % file_name)

	with open(file_path) as data_file:
		data = json.load(data_file)
		return data


def write_to_file(file_name, data):
	my_dir = os.path.dirname(__file__)
	file_path = os.path.join(my_dir, '../data/%s.json' % file_name)

	with open(file_path, "w") as jsonFile:
		json.dump(data, jsonFile)


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


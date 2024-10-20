from flask import Flask, request, jsonify, render_template
from scripts.fixtures import team_players_dict, player_names
from scripts.transfers import predictions, names_teams, player_points_dict

app = Flask(__name__, template_folder='../fpl_assist/templates', static_folder='../fpl_assist/static')

# Route for the home page
@app.route("/")
def home():
    return render_template('index.html')

# Route for the predicted points page
@app.route("/predicted-points")
def predicted_points():
    return render_template('predicted-points.html')

# Route for player stats page
@app.route("/player-stats")
def player_stats():
    return render_template('player-stats.html')

@app.route("/team-management")
def team_management():
    return render_template('team-management.html')

# Route to get the list of teams
@app.route("/api/teams", methods=['GET'])
def get_teams():
    teams = list(team_players_dict.keys())
    return jsonify(teams)

# Route to get the list of players from given team
@app.route("/api/players/<team_name>", methods=['GET'])
def get_players_from_team(team_name):
    players = team_players_dict[team_name]
    return jsonify(players)

# Route to get the list of players from the whole league
@app.route("/api/players", methods=['GET'])
def get_players():
    return jsonify(player_names)

@app.route("/api/predictedpoints/<player_name>", methods=['GET'])
def get_player_pred_points(player_name):
    gw = 7
    pred_points = predictions(gw)  # Get the DataFrame with predictions

    # Filter the DataFrame for the player
    filtered_points = pred_points[pred_points['name'].str.lower() == player_name.lower()]

    if not filtered_points.empty:
        points = filtered_points['points'].values[0]
        print(points)
        points = round(points, 2)
        return jsonify({'player_name': player_name, 'predicted_points': points, 'gw': gw})
    else:
        return jsonify({'error': 'Player not found'}), 404  # Return error if player not found

@app.route("/api/prices/<player_name>", methods=['GET'])
def get_player_prices(player_name):
    player_name = player_name.strip().lower()
    price = names_teams.loc[names_teams['name'].str.lower() == player_name, 'value'].values

    if price.size > 0:
        return jsonify({'Price':price[0]})
    else:
        print(f"{player_name} not found")

@app.route("/api/team/<player_name>", methods=['GET'])
def get_player_team(player_name):
    team = names_teams.loc[names_teams['name'].str.lower() == player_name, 'team'].values

    if team.size > 0:
        return jsonify({'Team':team[0]})
    else:
        print(f"{player_name} not found")

player_points_dict = {name.lower(): points for name, points in player_points_dict.items()}

@app.route("/api/past-points/<player_name>", methods=['GET'])
def get_past_points(player_name):
    past_points = player_points_dict[player_name]
    if past_points is not None:
        return jsonify({'PastPoints':past_points})
    else:
        return jsonify({'error': 'Player not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)
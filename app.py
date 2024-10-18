from flask import Flask, request, jsonify, render_template
from scripts.fixtures import team_players_dict, player_names
from scripts.transfers import predictions

app = Flask(__name__, template_folder='../fpl_assist/templates', static_folder='../fpl_assist/static')

# Route for the home page
@app.route("/")
def home():
    return render_template('index.html')

# Route for the player search page
@app.route("/player-search")
def player_search():
    return render_template('player-search.html')

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


if __name__ == "__main__":
    app.run(debug=True)
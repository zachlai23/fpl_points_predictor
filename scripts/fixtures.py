# Create a data structure with each team as the key and the value a list of their fixtures
import pandas as pd # type: ignore
from pprint import pprint
from pathlib import Path

# Constants
DATASETS_DIR = Path('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/24:25')
DROP_COLS_TEAMS = ['code', 'draw', 'form', 'loss', 'played', 'points', 
                        'position', 'team_division', 'unavailable', 
                        'win', 'strength_overall_home', 'strength_overall_away', 
                        'strength_attack_home', 'strength_attack_away', 
                        'strength_defence_home', 'strength_defence_away', 
                        'pulse_id']

# Create a dataframe of all player names
player_names_df = pd.read_csv(DATASETS_DIR / 'player_idlist.csv')
player_names_df['name'] = player_names_df['first_name'] + ' ' + player_names_df['second_name']
player_names_df = player_names_df[['name']]
player_names = player_names_df['name'].tolist()

# Create a dictionary of team(key), to list of all players on that team(value)
merged_gw = pd.read_csv(DATASETS_DIR / '24:25mergedGW.csv')
max_gameweek = merged_gw['GW'].max()
merged_gw = merged_gw[merged_gw['GW'] == max_gameweek]
team_players_dict = merged_gw.groupby('team')['name'].apply(list).to_dict()

# Create a dictionary of all teams mapped to their id
teams_df = (pd.read_csv(DATASETS_DIR / 'teams24:25.csv').drop(columns=DROP_COLS_TEAMS))
teams = teams_df['name'].tolist()
team_dict = teams_df.set_index('name')['id'].to_dict()

# Dictionary of team id mapped to their fixtures
# fixtures are in pairs of (oppenent team, opponent difficulty)
fixtures_df = pd.read_csv(DATASETS_DIR / 'fixtures.csv')
fixtures_df = fixtures_df.drop( ['code','event','finished','finished_provisional','id',
                                 'kickoff_time','minutes','provisional_start_time','started',
                                 'team_a_score','team_h_score','stats','pulse_id'], axis=1 )
fixtures = {team_id: [] for team_id in pd.concat([fixtures_df['team_h'], fixtures_df['team_a']]).unique()}
for index, row in fixtures_df.iterrows():
    # Add the away team to the home team's list with their difficulty
    fixtures[row['team_h']].append((row['team_a'], row['team_h_difficulty']))
    
    # Add the home team to the away team's list with their difficulty
    fixtures[row['team_a']].append((row['team_h'], row['team_a_difficulty']))

if __name__ == "__main__":
    pprint(team_players_dict)
    pprint(team_dict)
    pprint(fixtures)
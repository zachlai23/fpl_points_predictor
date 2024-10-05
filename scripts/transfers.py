# Choose which players to transfer in/out
from initial_team import *
import pandas as pd # type: ignore
from fpl_rf_prediction import *
from pprint import pprint
from fixtures import *

merged_gw = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/24:25/24:25mergedGW.csv')
df_sorted = merged_gw.sort_values(by=['name', 'GW'])
df_sorted['value'] = df_sorted['value'] / 10

# Group by player name and aggregate points for each gameweek
player_points_dict = df_sorted.groupby('name')['total_points'].apply(list).to_dict()

# Group by player name and minutes for each gameweek
player_mins_dict = df_sorted.groupby('name')['minutes'].apply(list).to_dict()

most_recent_gw = df_sorted['GW'].max()
df_most_recent = df_sorted[df_sorted['GW'] == most_recent_gw]
names_teams = df_most_recent[['name', 'team', 'value']]


# Update each players team(in case of transfer) and cost(price change)
for position in initial_squad:
    for player in position:
        name = player[1]
        index = names_teams[ names_teams['name'] == name ].index
        team = names_teams.loc[ index, 'team' ].item()
        value = names_teams.loc[ index, 'value' ].item()
        player.append( team )
        player[0] = value

# Function to Preprocess data for each position from the merged_gw csv file

def gk_merged_preprocess( gk_df ):
    gk_df, gk_name_mapping, gk_name_mapping_reverse = name_mapping( gk_df )
    gk_df['total_starts'] = gk_df.groupby('name')['starts'].transform('sum')

    gk_df['was_home'] = gk_df['was_home'].astype('category')
    gk_df['was_home'] = gk_df['was_home'].cat.codes

    # Take average of each feature from all gameweeks for each player
    columns_to_average = ['saves','ict_index','penalties_saved','goals_conceded','xP','clean_sheets','bps','minutes','expected_goals_conceded']
    averages = gk_df.groupby('name')[columns_to_average].transform('mean')
    averages.columns = [f'avg_{col}' for col in columns_to_average]
    gk_df[averages.columns] = averages

    gk_df['opponent_strength'] = None
    for index,row in gk_df.iterrows():
        team = row['team']
        difficulty = opponentDifficulty( team, 3 )
        row['opponent_strength'] = difficulty

    gk_df = gk_df.drop(['total_points', 'opponent_team','value','position','team','expected_goals_conceded','penalties_saved','bonus','own_goals','minutes','saves','kickoff_time','team_a_score','team_h_score','expected_assists','expected_goal_involvements','expected_goals','transfers_in','transfers_out','transfers_balance','fixture','assists','goals_scored','ict_index','influence','creativity','threat','penalties_missed','selected','goals_conceded','xP','clean_sheets','element','round','red_cards','yellow_cards','starts','bps' ],axis=1)
    gk_df.rename(columns={'avg_minutes': 'avg_mins',
                          'avg_ict_index': 'avg_ict',
                          'avg_clean_sheets': 'avg_cs',
                          'avg_expected_goals_conceded': 'avg_x_goals_conceded',
                          'avg_penalties_saved': 'avg_pen_saves'
                          }, inplace=True)
    gk_df = gk_df[['name', 'was_home', 'GW', 'avg_ict', 'avg_bps', 'avg_xP',
                    'total_starts', 'avg_mins', 'opponent_strength', 'avg_saves',
                    'avg_pen_saves', 'avg_goals_conceded', 'avg_cs', 'avg_x_goals_conceded']]
    gk_pred = gk_rf.predict( gk_df )
    return gk_pred, gk_df, gk_name_mapping

def def_merged_preprocess( def_df ):
    def_df, def_name_mapping, def_name_mapping_reverse = name_mapping( def_df )

    # Take sum of each feature from all gameweeks for each player
    def_df['total_assists'] = def_df.groupby('name')['assists'].transform('sum')
    def_df['total_goals'] = def_df.groupby('name')['goals_scored'].transform('sum')
    def_df['total_cs'] = def_df.groupby('name')['clean_sheets'].transform('sum')
    def_df['total_starts'] = def_df.groupby('name')['starts'].transform('sum')

    def_df['was_home'] = def_df['was_home'].astype('category')
    def_df['was_home'] = def_df['was_home'].cat.codes


    columns_to_average = ['ict_index','bps','xP','expected_assists','expected_goal_involvements', 'goals_conceded', 'expected_goals_conceded', 'minutes']
    averages = def_df.groupby('name')[columns_to_average].transform('mean')
    averages.columns = [f'avg_{col}' for col in columns_to_average]
    def_df[averages.columns] = averages

    def_df['opponent_strength'] = None
    for index,row in def_df.iterrows():
        team = row['team']
        difficulty = opponentDifficulty( team, 3 )
        row['opponent_strength'] = difficulty

    def_df = def_df.drop(['total_points', 'opponent_team','value','position','team','starts','minutes','goals_conceded','red_cards','team_a_score','team_h_score','yellow_cards','element','assists','goals_scored','clean_sheets','penalties_missed','penalties_saved','influence','threat','round','saves','selected','threat','kickoff_time','own_goals','fixture','creativity','transfers_balance','transfers_in','transfers_out','ict_index','bps','bonus','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded'],axis=1)    
    def_df.rename(columns={'avg_minutes': 'avg_mins',
                          'avg_ict_index': 'avg_ict',
                          'avg_clean_sheets': 'avg_cs',
                          'avg_expected_goals_conceded': 'avg_xGC',
                          'avg_expected_assists': 'avg_xA',
                          'avg_expected_goal_involvements': 'avg_xGI',
                          'avg_goals_conceded': 'avg_GC'
                          }, inplace=True)
    def_df = def_df[['name', 'was_home', 'GW', 'avg_ict', 'avg_bps', 'avg_xP',
       'total_starts', 'avg_mins', 'opponent_strength', 'avg_xA', 'avg_xGI',
       'avg_xGC', 'avg_GC', 'total_assists', 'total_goals', 'total_cs']]
    def_pred = def_rf.predict( def_df )
    return def_pred, def_df, def_name_mapping


def mid_merged_preprocess(mid_df):
    mid_df, mid_name_mapping, mid_name_mapping_reverse = name_mapping( mid_df )

    mid_df['total_assists'] = mid_df.groupby('name')['assists'].transform('sum')
    mid_df['total_goals'] = mid_df.groupby('name')['goals_scored'].transform('sum')
    mid_df['total_cs'] = mid_df.groupby('name')['clean_sheets'].transform('sum')
    mid_df['total_starts'] = mid_df.groupby('name')['starts'].transform('sum')

    mid_df['was_home'] = mid_df['was_home'].astype('category')
    mid_df['was_home'] = mid_df['was_home'].cat.codes

    columns_to_average = ['ict_index','goals_scored', 'bps','xP','expected_assists', 'expected_goals', 'expected_goal_involvements', 'goals_conceded', 'expected_goals_conceded', 'minutes']
    averages = mid_df.groupby('name')[columns_to_average].transform('mean')
    averages.columns = [f'avg_{col}' for col in columns_to_average]
    mid_df[averages.columns] = averages

    mid_df['opponent_strength'] = None
    for index,row in mid_df.iterrows():
        team = row['team']
        difficulty = opponentDifficulty( team, 3 )
        row['opponent_strength'] = difficulty

    mid_df = mid_df.drop(['total_points', 'opponent_team','value','position','team','starts','minutes','goals_conceded','red_cards','team_a_score','team_h_score','yellow_cards','element','assists','goals_scored','clean_sheets','penalties_missed','penalties_saved','influence','threat','round','saves','selected','threat','kickoff_time','own_goals','fixture','creativity','transfers_balance','transfers_in','transfers_out','ict_index','bps','bonus','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded'],axis=1)    
    mid_df.rename(columns={'avg_minutes': 'avg_mins',
                          'avg_ict_index': 'avg_ict',
                          'avg_clean_sheets': 'avg_cs',
                          'avg_expected_goals_conceded': 'avg_xGC',
                          'avg_expected_assists': 'avg_xA',
                          'avg_expected_goal_involvements': 'avg_xGI',
                          'avg_goals_conceded': 'avg_GC',
                          'avg_expected_goals': 'avg_xG'
                          }, inplace=True)

    mid_df = mid_df[['name', 'was_home', 'GW', 'avg_ict', 'avg_bps', 'avg_xP',
       'total_starts', 'avg_mins', 'opponent_strength', 'avg_xA', 'avg_xG',
       'avg_xGI', 'avg_xGC', 'avg_GC', 'total_assists', 'total_goals',
       'total_cs']]
    mid_pred = mid_rf.predict( mid_df )
    return mid_pred, mid_df, mid_name_mapping

def fwd_merged_preprocess(fwd_df):
    fwd_df, fwd_name_mapping, fwd_name_mapping_reverse = name_mapping( fwd_df )

    fwd_df['total_assists'] = fwd_df.groupby('name')['assists'].transform('sum')
    fwd_df['total_goals'] = fwd_df.groupby('name')['goals_scored'].transform('sum')
    fwd_df['total_starts'] = fwd_df.groupby('name')['starts'].transform('sum')

    fwd_df['was_home'] = fwd_df['was_home'].astype('category')
    fwd_df['was_home'] = fwd_df['was_home'].cat.codes

    columns_to_average = ['ict_index', 'goals_scored', 'bps', 'xP', 'expected_assists', 'expected_goals', 'expected_goal_involvements', 'minutes']
    averages = fwd_df.groupby('name')[columns_to_average].transform('mean')
    averages.columns = [f'avg_{col}' for col in columns_to_average]
    fwd_df[averages.columns] = averages

    fwd_df['opponent_strength'] = None
    for index,row in fwd_df.iterrows():
        team = row['team']
        difficulty = opponentDifficulty( team, 3 )
        row['opponent_strength'] = difficulty

    fwd_df = fwd_df.drop(['total_points', 'opponent_team','value','position','team','transfers_balance','bonus','own_goals','saves','team_a_score','team_h_score','red_cards','yellow_cards','transfers_in','transfers_out','penalties_missed','penalties_saved','clean_sheets','creativity','influence','threat','kickoff_time','fixture','round','element','starts','selected','ict_index','assists','goals_scored','bps','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded','goals_conceded','minutes'],axis=1)
    fwd_df.rename(columns={'avg_minutes': 'avg_mins',
                           'avg_goals_scored': 'avg_goals',
                          'avg_ict_index': 'avg_ict',
                          'avg_expected_assists': 'avg_xA',
                          'avg_expected_goal_involvements': 'avg_xGI',
                          'avg_expected_goals': 'avg_xG'
                          }, inplace=True)
    fwd_df = fwd_df[['name', 'was_home', 'GW', 'avg_ict', 'avg_bps', 'avg_xP',
       'total_starts', 'avg_mins', 'opponent_strength', 'avg_xA', 'avg_xG',
       'avg_xGI', 'total_assists', 'total_goals']]
    fwd_pred = fwd_rf.predict( fwd_df )
    return fwd_pred, fwd_df, fwd_name_mapping

def combine_pred_dfs(X, pred, name_mapping, pos):
    pred_df = pd.DataFrame( pred, columns=['points'] )
    pred_df = pred_df.reset_index(drop=True)
    X = X.reset_index(drop=True)
    combined_df = pd.concat( [ X, pred_df], axis=1 )
    temp_df = combined_df[ combined_df['GW'] == 1 ]
    points = temp_df[ ['name', 'points'] ]
    for name in points['name']:
        points['name'] = points['name'].replace( name, name_mapping[name] )
    points['position'] = pos
    points = points.sort_values( by='points', ascending = False )
    return points


# # Run model to get predictions for the upcoming gameweek based on merged_gw.csv
def predictions( gw ):
    df = pd.read_csv( '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/24:25/24:25mergedGW.csv' )

    gk_df = df[df['position'] == 'GK']
    def_df = df[df['position'] == 'DEF']
    mid_df = df[df['position'] == 'MID']
    fwd_df = df[df['position'] == 'FWD']

    gk_pred, gk_X, gk_name_mapping = gk_merged_preprocess(gk_df)
    def_pred, def_X, def_name_mapping = def_merged_preprocess(def_df)
    mid_pred, mid_X, mid_name_mapping = mid_merged_preprocess(mid_df)
    fwd_pred, fwd_X, fwd_name_mapping = fwd_merged_preprocess(fwd_df)

    gk_points = combine_pred_dfs(gk_X, gk_pred, gk_name_mapping, 'gk')
    def_points = combine_pred_dfs(def_X, def_pred, def_name_mapping, 'def')
    mid_points = combine_pred_dfs(mid_X, mid_pred, mid_name_mapping, 'mid')
    fwd_points = combine_pred_dfs(fwd_X, fwd_pred, fwd_name_mapping, 'fwd')

    # Merge all point predictions together
    full_points = pd.concat( [ gk_points, def_points, mid_points, fwd_points ], axis=0, ignore_index=True )
    full_points = full_points.sort_values( by='points', ascending = False )

    return full_points

def squad_predictions(gw):
    points_df = predictions(gw)
    for position in initial_squad:
        for player in position:
            name = player[1]
            index = points_df[ points_df['name'] == name ].index
            points = points_df.loc[ index, 'points' ].item()
            player[2] = points
        position.sort(key=lambda player: player[2], reverse=True)
        
def weeklyRecs( squad ):
    starters, bench = startingXI( squad )
    starters = sorted( starters, key=lambda x: ('gk', 'def', 'mid', 'fwd').index(x[3])  )    
    bench = sorted( bench, key=lambda x: x[2], reverse=True )

    for position in initial_squad:
        for player in position:
            player.pop(2)

    value = squadValue( squad )
    value = round( value, 1 )

    # team_points = totalPoints( starters )

    captains = chooseCaptain( starters )
    captain, vice_captain = captains[0], captains[1]

    print( "\nGameweek 3\n----------------------------")
    print( "\nStarting XI:\n----------------------" )
    pprint( starters )
    print( "\nBench\n-----------------------")
    pprint( bench )
    print( "\nCaptain: ", captain[1] )
    print( "Vice Captain: ", vice_captain[1] )
    # print( '\nTotal predicted points: ', team_points )
    print( '\nSquad value: ', value, '\n' )


# Take sum of next four matches difficulties
def strengthOfSchedule( gw, team ):
    team_id = team_dict[team]
    sum = 0
    for i in range( gw-1, gw+3 ):
        sum = sum + fixtures[team_id][i][1]
    return sum

# Return an opponent team difficulty given team and gameweek
def opponentDifficulty( team, gw ):
    team_id  = team_dict[team]
    difficulty = fixtures[team_id][gw-1][1]
    return difficulty

# Take sum of point returns from last four matches
def recentForm( name, playerPoints, gw ):
    sumPoints = 0
    if gw == 2:
        return playerPoints[name]
    elif gw > 4: 
        for i in range(4):
            sumPoints = sumPoints + playerPoints[name][i]
    else:
        for points in playerPoints[name]:
            sumPoints = sumPoints + points
    return sumPoints


# Return top 20 players that have earned most points in last four weeks
def findBestPlayers( gw, merged_gw=df_most_recent ):
    top_players = []
    for index,row in merged_gw.iterrows():
        player = []
        name = row['name']
        team = row['team']
        recent_form = recentForm( name, player_points_dict, gw )
        player.append( name )
        player.append( row['position'] )
        player.append( team )
        player.append( row['value'] )
        # player.append( recent_form )
        schedule_strength = strengthOfSchedule( 2, team )
        # player.append( schedule_strength )
        player.append( point_schedule_ratio(recent_form, schedule_strength))
        top_players.append(player)
    top_players = sorted( top_players, key=lambda x: x[4], reverse=True )
    top_20 = top_players[:20]
    return top_20

def findWorstPlayers(gw, squad):
    worstPlayers = {}
    for position in squad:
        for player in position:
            name = player[1]
            sumPoints = 0
            pointList = player_points_dict[name]
            stop = max(0, len(pointList)-4)
            for i in range(len(pointList)-1, stop-1, -1):
                sumPoints = sumPoints + pointList[i]
            worstPlayers[name] = sumPoints
            worstPlayers = dict(sorted(worstPlayers.items(), key=lambda item: item[1]))
    return min(gw-1, 4), worstPlayers

# Return a dict of players names and minutes played from last 4 games
def minutesPlayed(gw, squad):
    squadMins = {}
    n = min(gw-1,4)
    for position in squad:
        for player in position:
            name = player[1]
            minsList = player_mins_dict[name]
            squadMins[name] = minsList[-n:]
            squadMins = dict(sorted(squadMins.items(), key=lambda item: item[1]))
    return min(gw-1, 4), squadMins


# Return point to schedule ratio of players
def point_schedule_ratio( recentForm, scheduleStrength ):
    ratio = recentForm / scheduleStrength
    ratio = round( ratio, 1 )
    return ratio

# Find players to transfer out of team
#   features considered: minutes played, points scored, strength of schedule
def playersOut(gw, squad):
    transferOut = []
    recent_form = {}
    # Add players with 0 minutes played in last 4 games
    gws, minsPlayed = minutesPlayed(gw, squad)
    for key, value in minsPlayed.items():
        sumMins = 0
        for i in value:
            sumMins = sumMins + i
        if sumMins == 0:
            transferOut.append(key)
    # Add players with >=4 points scored in the last 4 weeks
    for position in squad:
        for player in position:
            name = player[1]
            form = recentForm(name, player_points_dict, gw)
            recent_form[name] = form

            index = names_teams[ names_teams['name'] == name ].index
            team = names_teams.loc[ index, 'team' ].item()
            schedStrength = strengthOfSchedule(gw, team)
            print(name, schedStrength)
    for key, value in recent_form.items():
        if value <= 4 and key not in transferOut:
            transferOut.append(key)        
    pprint(transferOut)


if __name__ == "__main__":
    squad_predictions( 3 )
    weeklyRecs(initial_squad)
#     pprint( findBestPlayers( 3, df_most_recent ) )

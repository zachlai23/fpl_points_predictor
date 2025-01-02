# Picking the best initial team based off previous seasons statistics
from .fpl_rf_prediction import *
from .pick_team import *
import pandas as pd # type: ignore
from .fixtures import *

POS_SORTED = Path('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted')


# Return list of names from the current season to eliminate players who transferred out of the league
def name_list( pos_X_test, name_mapping, pos ):
    current_season = pos_X_test[pos_X_test['GW'] == 1]
    current_season['name'] = current_season['name'].map(name_mapping)
    current_season_list = current_season[['name']]
    current_season_list['position'] = pos
    return current_season_list

# Return list of names from current season, based off 'cleaned_players.csv'
def name_list_2( cleaned_players_df ):
    names = cleaned_players_df[[ 'first_name', 'second_name', 'now_cost', 'element_type' ]]
    names['name'] = names['first_name'] + ' ' + names['second_name']
    names.drop(['first_name', 'second_name'], axis=1, inplace=True )
    names['now_cost'] = names['now_cost'] / 10
    names['position'] = names['element_type'].str.lower()
    return names

# Create dataframe with players name and predicted points for gw 38
def prev_season_data( pos_pred, pos_X, name_mapping ):
    pred_df = pd.DataFrame( pos_pred, columns=['points'] )
    combined_df = pd.concat( [pos_X, pred_df], axis=1 )
    temp_df = combined_df[ combined_df['GW'] == 38 ]
    df2 = temp_df[ ['name','points'] ]
    df2['name'] = df2['name'].map(name_mapping)
    return df2

def process_init_df(df, pos):
    df = pd.read_csv( df )
    df, name_map, _ = name_mapping(df)
    df, _ = position_preprocess(df, pos)
    df = df.drop(['Unnamed: 0', 'total_points'],axis=1)
    return df, name_map

def predict_points(df, model, name_mapping):
    pred = model.predict(df)
    return prev_season_data(pred, df, name_mapping)

def chooseInitialTeam(df):
    position_requirements = {'gk': 2, 'def': 5, 'mid': 5, 'fwd': 3}
    position_filled = {pos: 0 for pos in position_requirements}
    iss = []
    total_cost = 60

    i = 1
    team_count = {}
    for team in teams:
        team_count[team] = 0

    # add player with highest predicted points if position is needed and he fits under the budget leaving enough for other players
    for index,row in df.iterrows():
        pos = row['position']
        if i % 4 == 1:
            i += 1
            if pos == 'fwd' and position_filled[pos] < position_requirements[pos] and total_cost + ( row['value'] - 4 ) <= 100:
                position_filled[pos] += 1
                total_cost += row['value'] - 4
                iss.append(row)
        elif i % 4 == 2:
            i += 1
            if pos == 'mid' and position_filled[pos] < position_requirements[pos] and total_cost + ( row['value'] - 4 ) <= 100:
                position_filled[pos] += 1
                total_cost += row['value'] - 4
                iss.append(row)
        elif i % 4 == 3:
            i += 1
            if pos == 'def' and position_filled[pos] < position_requirements[pos] and total_cost + ( row['value'] - 4 ) <= 100:
                position_filled[pos] += 1
                total_cost += row['value'] - 4
                iss.append(row)
        elif i % 4 == 0:
            i += 1
            if pos == 'gk' and position_filled[pos] < position_requirements[pos] and total_cost + ( row['value'] - 4 ) <= 100:
                position_filled[pos] += 1
                total_cost += row['value'] - 4
                iss.append(row)

    gk = []
    mid = []
    defs = []
    fwd = []

    init_squad = []
    # convert numerical codes to names
    for elem in iss:
        list = []
        for item in elem:
            list.append(item)
        if elem['position'] == 'gk':
            gk.append(list)
        elif elem['position'] == 'def':
            defs.append(list)
        elif elem['position'] == 'mid':
            mid.append(list)
        else:
            fwd.append(list)
    init_squad.append(gk)
    init_squad.append(defs)
    init_squad.append(mid)
    init_squad.append(fwd)
    return init_squad

# Choosing initial team based off statistics from last season, does not include incoming players from other leagues
def initialTeam( gk_df, def_df, mid_df, fwd_df, cleaned_players ):
    # Load and preprocess data for each position
    gk_init, gk_init_name_mapping = process_init_df(gk_df, 'gk')
    def_init, def_init_name_mapping = process_init_df(def_df, 'def')
    mid_init, mid_init_name_mapping = process_init_df(mid_df, 'mid')
    fwd_init, fwd_init_name_mapping = process_init_df(fwd_df, 'fwd')

    # Run predictions
    gk2_df = predict_points( gk_init, gk_rf, gk_init_name_mapping )
    def2_df = predict_points( def_init, def_rf, def_init_name_mapping )
    mid2_df = predict_points( mid_init, mid_rf, mid_init_name_mapping )
    fwd2_df = predict_points( fwd_init, fwd_rf, fwd_init_name_mapping )

    # Create one dataframe with players' names & predicted points
    prev_season_df = pd.concat( [ gk2_df, def2_df, mid2_df, fwd2_df ], ignore_index = True )

    cleaned_players_df = pd.read_csv( cleaned_players )
    names = name_list_2( cleaned_players_df )

    # Merge with previous points
    prev_points = pd.merge(names, prev_season_df, on='name', how='left').fillna(0)
    prev_points.rename(columns={'now_cost': 'value'}, inplace=True)

    # Separate by position
    position_data = {pos: prev_points[prev_points['position'] == pos][['value', 'name', 'points', 'position']]
                     .sort_values(by='points', ascending=False) for pos in ['gk', 'def', 'mid', 'fwd']}
    
    # Concatenate all positions for selection
    all_players = pd.concat(position_data.values(), ignore_index=True)

    return chooseInitialTeam(all_players)

initial_squad = initialTeam( POS_SORTED / 'goalkeepers_test.csv', POS_SORTED / 'defenders_test.csv', POS_SORTED / 'midfielders_test.csv', POS_SORTED / 'forwards_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/24:25/cleaned_players24:25.csv' )

init_starters, init_bench = startingXI( initial_squad )
init_starters = sorted( init_starters, key=lambda x: ('gk', 'def', 'mid', 'fwd').index(x[3])  )    
init_bench = sorted( init_bench, key=lambda x: x[2], reverse=True )

value = squadValue( initial_squad )
value = round( value, 1 )

team_points = totalPoints( init_starters )

captains = chooseCaptain( init_starters )
captain, vice_captain = captains[0], captains[1]

if __name__=="__main__":
    pprint(initial_squad)
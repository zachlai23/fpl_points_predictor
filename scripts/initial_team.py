from .mult_seasons_attempt import *
from .pick_team import startingXI, teams
import pandas as pd

# Return list of names from the current season to eliminate players who transferred out of the league
def name_list( pos_X_test, name_mapping, pos ):
    current_season = pos_X_test[pos_X_test['GW'] == 1]
    current_season['name'] = current_season['name'].map(name_mapping)
    current_season_list = current_season[['name']]
    current_season_list['position'] = pos
    return current_season_list


# Create dataframe with players name and predicted points for gw 38
def prev_season_data( pos_pred, pos_X, name_mapping ):
    pred_df = pd.DataFrame( pos_pred, columns=['points'] )
    combined_df = pd.concat( [pos_X, pred_df], axis=1 )
    temp_df = combined_df[ combined_df['GW'] == 38 ]
    df2 = temp_df[ ['name','points'] ]
    df2['name'] = df2['name'].map(name_mapping)
    return df2

# if __name__ == "__main__":
def chooseInitialTeam( gk_df, def_df, mid_df, fwd_df ):
    gk_df2 = pd.read_csv( gk_df )
    gk_df2, gk2_name_mapping, gk2_name_mapping_reverse = name_mapping( gk_df2 )
    gk_df2, gk2_value = gk_preprocess( gk_df2 )
    gk_df2 = gk_df2.drop(['Unnamed: 0'],axis=1)

    def_df2 = pd.read_csv( def_df )
    def_df2, def2_name_mapping, def2_name_mapping_reverse = name_mapping( def_df2 )
    def_df2, def2_value = def_preprocess( def_df2 )
    def_df2 = def_df2.drop(['Unnamed: 0'],axis=1)

    mid_df2 = pd.read_csv( mid_df )
    mid_df2, mid2_name_mapping, mid2_name_mapping_reverse = name_mapping( mid_df2 )
    mid_df2, mid2_value = mid_preprocess( mid_df2 )
    mid_df2 = mid_df2.drop(['Unnamed: 0'],axis=1)

    fwd_df2 = pd.read_csv( fwd_df )
    fwd_df2, fwd2_name_mapping, fwd2_name_mapping_reverse = name_mapping( fwd_df2 )
    fwd_df2, fwd2_value = fwd_preprocess( fwd_df2 )
    fwd_df2 = fwd_df2.drop(['Unnamed: 0'],axis=1)

    gk2_X = gk_df2.drop( ['total_points'], axis=1 )
    def2_X = def_df2.drop( ['total_points'], axis=1 )
    mid2_X = mid_df2.drop( ['total_points'], axis=1 )
    fwd2_X = fwd_df2.drop( ['total_points'], axis=1 )

    gk2_pred = gk_rf.predict( gk2_X )
    def2_pred = def_rf.predict( def2_X )
    mid2_pred = mid_rf.predict( mid2_X )
    fwd2_pred = fwd_rf.predict( fwd2_X )

    # Create one dataframe with players' names & predicted points
    gk2_df = prev_season_data( gk2_pred, gk2_X, gk2_name_mapping )
    def2_df = prev_season_data( def2_pred, def2_X, def2_name_mapping )
    mid2_df = prev_season_data( mid2_pred, mid2_X, mid2_name_mapping )
    fwd2_df = prev_season_data( fwd2_pred, fwd2_X, fwd2_name_mapping )
    prev_df = pd.concat( [ gk2_df, def2_df, mid2_df, fwd2_df ], ignore_index = True )

    # Create one list of all names from current season
    current_season_gk_list = name_list( gk_X_test, gk_test_name_mapping, 'gk' )
    current_season_def_list = name_list( def_X_test, def_test_name_mapping, 'def' )
    current_season_mid_list = name_list( mid_X_test, mid_test_name_mapping, 'mid' )
    current_season_fwd_list = name_list( fwd_X_test, fwd_test_name_mapping, 'fwd' )
    player_list = pd.concat( [ current_season_gk_list, current_season_def_list, current_season_mid_list, current_season_fwd_list ], ignore_index = True )

    gw_1_price = price_df[price_df['GW'] == 1]
    gw_1_price = gw_1_price.drop( ['GW','position'], axis=1 )

    player_list = pd.merge( player_list, gw_1_price, on='name', how='left' )

    # Create dataframe with players from previous season who are in the current season
    prev_points = pd.merge( player_list, prev_df, on='name', how='left')
    prev_points['points'] = prev_points['points'].fillna(0)


    prev_points_gk = prev_points[prev_points['position'] == 'gk']
    prev_points_def = prev_points[prev_points['position'] == 'def']
    prev_points_mid = prev_points[prev_points['position'] == 'mid']
    prev_points_fwd = prev_points[prev_points['position'] == 'fwd']

    prev_points_gk = prev_points_gk[['value', 'name', 'team', 'points', 'position']]
    prev_points_def = prev_points_def[['value', 'name', 'team', 'points', 'position']]
    prev_points_mid = prev_points_mid[['value', 'name', 'team', 'points', 'position']]
    prev_points_fwd = prev_points_fwd[['value', 'name', 'team', 'points', 'position']]

    prev_points_gk = prev_points_gk.sort_values( by='points', ascending=False )
    prev_points_def = prev_points_def.sort_values( by='points', ascending=False )
    prev_points_mid = prev_points_mid.sort_values( by='points', ascending=False )
    prev_points_fwd = prev_points_fwd.sort_values( by='points', ascending=False )

    # Dropping players who were selected but transferred to another league
    drop_index = prev_points_fwd[prev_points_fwd['name'] == 'Harry Kane'].index
    prev_points_fwd = prev_points_fwd.drop( drop_index )
    drop_index = prev_points_mid[prev_points_mid['name'] == 'Granit Xhaka'].index
    prev_points_mid = prev_points_mid.drop( drop_index )

    # Pick the initial team of 15 players
    position_requirements = { 'gk':2, 'def':5, 'mid':5, 'fwd':3 }
    position_filled = { 'gk':0, 'def':0, 'mid':0, 'fwd':0 }
    iss = []
    total_cost = 60
    gk, fwd, mid, defs = 0, 1, 2, 3
    df = pd.concat( [ prev_points_gk, prev_points_def, prev_points_mid, prev_points_fwd ] )

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

initial_squad = chooseInitialTeam( '/Users/zacharylai/Desktop/df2/gk_df2.csv', '/Users/zacharylai/Desktop/df2/def_df2.csv', '/Users/zacharylai/Desktop/df2/mid_df2.csv', '/Users/zacharylai/Desktop/df2/fwd_df2.csv' )
# initial_squad2 = chooseInitialTeam( '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/goalkeepers_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/defenders_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/midfielders_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/forwards_test.csv')
init_starters, init_bench = startingXI( initial_squad )
init_starters = sorted( init_starters, key=lambda x: ('gk', 'def', 'mid', 'fwd').index(x[4])  )    
init_bench = sorted( init_bench, key=lambda x: x[3], reverse=True )

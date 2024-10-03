# Includes functions for picking the best team/starters considering predicted points and budget
from pprint import pprint
from .mult_seasons_attempt import *
import pandas as pd # type: ignore

def lookup( name_mapping, X_test, y_test, pred ):
        pprint( name_mapping )
        id = int( input( "Select an id for a player: " ) )
        gw = int( input( "Enter a game week 1-38: " ) )
        index = X_test.loc[ ( X_test['name'] == id ) & ( X_test['GW'] == gw ) ].index
        print( name_mapping[id], "predicted points for gameweek ", gw, ": ", pred[index] )
        print( name_mapping[id], "actual points for gameweek ", gw, ": ", y_test[index] )


# Function to look up players predicted and actual points for a given gameweek
def lookupPlayer():
    position = input( "Select a position( 'gk', 'def', 'mid', 'fwd' ): " )
    if position == 'gk':
        lookup( gk_test_name_mapping, gk_X_test, gk_y_test, gk_pred )
    elif position == 'def':
        lookup( def_test_name_mapping, def_X_test, def_y_test, def_pred )
    elif position == 'mid':
        lookup( mid_test_name_mapping, mid_X_test, mid_y_test, mid_pred )
    elif position == 'fwd':
        lookup( fwd_test_name_mapping, fwd_X_test, fwd_y_test, fwd_pred )


# Add price to a players list in the team selection
def add_price( price_df, gw_df, name_mapping, name_mapping_reverse ):
    price_df = price_df.drop(['position'],axis=1)
    # convert names in price dataframes to numerical representations
    for name in price_df['name']:
        price_df['name'] = price_df['name'].replace( name, name_mapping_reverse[name] )

    # merge the price and gameweek dataframe into one sharing the name columns
    res = pd.merge( price_df, gw_df, on='name' )
    return res


# return dataframe the combines names and points for the given gameweek
def combine_dfs( pred, X_test, price_df, gw, pos, name_mapping, name_mapping_reverse ):
    pred_df = pd.DataFrame( pred, columns=['points'] )
    combined_df = pd.concat( [X_test, pred_df], axis=1 )
    temp_df = combined_df[ combined_df['GW'] == gw ]
    gameweek_df = temp_df[ ['name','points'] ]
    gameweek_df['position'] = pos

    gameweek_df = gameweek_df.groupby(['name', 'position' ], as_index=False)['points'].sum()

    price_df = price_df[price_df['GW']==gw]
    price = price_df[price_df['position'] == pos.upper()]
    price_combined = add_price( price, gameweek_df, name_mapping, name_mapping_reverse )
    sorted = price_combined.sort_values( by='points', ascending = False )
    return sorted


# return the top 15 players predicted to perform in the given gameweek using a budget of 100 pounds
def combination( gk, defs, mid, fwd, gk_map, def_map, mid_map, fwd_map, budget ):
    df = pd.concat( [ gk, defs, mid, fwd ] )
    position_requirements = { 'gk':2, 'def':5, 'mid':5, 'fwd':3 }
    position_filled = { 'gk':0, 'def':0, 'mid':0, 'fwd':0 }
    best = []
    total_cost = 0
    df = df.sort_values(by='points', ascending=False)
    players = [ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4.5, 4.5, 4.3 ]

    team_count = {}
    for team in teams:
        team_count[team] = 0
    
    i=0
    # add player with highest predicted points if position is needed and he fits under the budget leaving enough for other players
    for index,row in df.iterrows():
        pos = row['position']
        total = sum(players)
        total = round( total, 1 )
        if position_filled[pos] < position_requirements[pos] and total + (row['value']-4) <= budget and team_count[row['team']] < 3:
            best.append( row )         
            position_filled[pos] += 1
            players[i] = row['value']
            total_cost += ( row['value'] )
            total_cost = round( total_cost, 1 )
            team_count[row['team']] += 1
            i+=1
                
    gk = []
    mid = []
    defs = []
    fwd = []

    best15 = []
    # convert numerical codes to names
    for elem in best:
        list = []
        for item in elem:
            list.append(item)
        if elem['position'] == 'gk':
            list[1] = gk_map[list[1]]
            gk.append(list)
        elif elem['position'] == 'def':
            list[1] = def_map[list[1]]
            defs.append(list)
        elif elem['position'] == 'mid':
            list[1] = mid_map[list[1]]
            mid.append(list)
        else:
            list[1] = fwd_map[list[1]]
            fwd.append(list)
    best15.append(gk)
    best15.append(defs)
    best15.append(mid)
    best15.append(fwd)
    return best15


# Picks the top 15 players( 2 gk, 5 def, 5 mid, 3 fwd ) you can have in your team under the budget of 100 pounds
def bestPossibleTeam( gw ):
    gk = combine_dfs( gk_pred, gk_X_test, price_df, gw, 'gk', gk_test_name_mapping, gk_test_name_mapping_reverse )
    defs = combine_dfs( def_pred, def_X_test, price_df, gw, 'def', def_test_name_mapping, def_test_name_mapping_reverse )
    mid = combine_dfs( mid_pred, mid_X_test, price_df, gw, 'mid', mid_test_name_mapping, mid_test_name_mapping_reverse )
    fwd = combine_dfs( fwd_pred, fwd_X_test, price_df, gw, 'fwd', fwd_test_name_mapping, fwd_test_name_mapping_reverse )

    gk_df = gk[['value', 'name', 'team', 'points', 'position']]
    def_df = defs[['value', 'name', 'team', 'points', 'position']]
    mid_df = mid[['value', 'name', 'team', 'points', 'position']]
    fwd_df = fwd[['value', 'name', 'team', 'points', 'position']]
    
    return combination( gk_df, def_df, mid_df, fwd_df, gk_test_name_mapping, def_test_name_mapping, mid_test_name_mapping, fwd_test_name_mapping, 100 )


# Picks the best possible starting eleven given the 15 players chosen for the team
def startingXI( best15 ):
    starting11 = []
    bench4 = []
    # Find starting gk
    starting11.append( best15[0][0] )
    gk =  best15[0][1]

    # Top 3 defenders
    starting11.append( best15[1][0] )
    starting11.append( best15[1][1] )
    starting11.append( best15[1][2] )
    bench4.append( best15[1][3] )
    bench4.append( best15[1][4] )

    # Top 2 mids
    starting11.append( best15[2][0] )
    starting11.append( best15[2][1] )
    bench4.append( best15[2][2] )
    bench4.append( best15[2][3] )
    bench4.append( best15[2][4] )

    # Top Forward
    starting11.append( best15[3][0] )
    bench4.append( best15[3][1] )
    bench4.append( best15[3][2] )

    # Next 4 highest players
    bench_sorted = sorted(bench4, key=lambda x: x[2], reverse=True)
    top4 = bench_sorted[:4]
    for player in top4:
        starting11.append( player )
        bench4.remove( player )
    bench4.append(gk)
    return starting11, bench4


# Return value of squad
def squadValue( squad ):
    value = 0
    for position in squad:
        for player in position:
            # print( player[3] )
            value += player[0]
    return value


# Return total predicted points for squad
def totalPoints( squad ):
    total_points = 0
    for player in squad:
        total_points += player[2]
    return total_points

def chooseCaptain( squad ):
    squad_sorted = sorted(squad, key=lambda x: x[2], reverse=True)
    captains = squad_sorted[:2]
    return captains
# from scripts import mult_seasons_attempt
from scripts import pick_team
from scripts import initial_team
import pandas as pd
from pprint import pprint

# Print best predicted team for each gameweek, recommended starting XI, and squad value
# Test with players from last season

initial_squad_2 = initial_team.chooseInitialTeam( '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/goalkeepers_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/defenders_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/midfielders_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/forwards_test.csv', '/Users/zacharylai/Desktop/fpl_points_predictor/datasets/24:25/cleaned_players24:25.csv' )
init_starters, init_bench = pick_team.startingXI( initial_squad_2 )
init_starters = sorted( init_starters, key=lambda x: ('gk', 'def', 'mid', 'fwd').index(x[3])  )    
init_bench = sorted( init_bench, key=lambda x: x[2], reverse=True )

value = pick_team.squadValue( initial_squad_2 )
value = round( value, 1 )

team_points = pick_team.totalPoints( init_starters )

captains = pick_team.chooseCaptain( init_starters )
captain, vice_captain = captains[0], captains[1]


print( "\nGameweek 1\n----------------------------")
print( "\nStarting XI:\n----------------------" )
pprint( init_starters )
print( "\nBench\n-----------------------")
pprint( init_bench )
print( "/nCaptain: ", captain[1] )
print( "Vice Captain: ", vice_captain[1] )
print( '\nTotal predicted points: ', team_points )
print( '\nSquad value: ', value )

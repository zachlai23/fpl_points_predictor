# from scripts import mult_seasons_attempt
from scripts import pick_team
from scripts import initial_team
import pandas as pd
from pprint import pprint

# Print best predicted team for each gameweek, recommended starting XI, and squad value
# Test with players from last season
print( "\nGameweek 1\n----------------------------")
print( "\nStarting XI:\n----------------------" )
pprint( initial_team.init_starters )
print( "\nBench\n-----------------------")
pprint( initial_team.init_bench )

for week in range( 2, 39 ):
    print( "\nGameweek ", week, '\n----------------------------')
    squad = pick_team.bestPossibleTeam(week)
    value = pick_team.squadValue( squad )
    value = round( value, 1 )
    starters, bench = pick_team.startingXI( squad )
    team_points = pick_team.totalPoints( starters )
    print( "\nStarting XI:\n----------------------" )
    starters = sorted( starters, key=lambda x: ('gk', 'def', 'mid', 'fwd').index(x[4])  )    
    bench = sorted( bench, key=lambda x: x[3], reverse=True)
    for player in starters:
        print( player )
    print( "\nBench\n----------------------- " )
    for player in bench:
        print( player )
    print( '\nTotal predicted points: ', team_points )
    print( '\nSquad value: ', value )
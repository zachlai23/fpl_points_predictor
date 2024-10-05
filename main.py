from scripts import initial_team
from scripts import transfers
import pandas as pd
from pprint import pprint


gw = 3
choice = int(input( "\n1) View team's points scored\n2) View recommended team\n3) Find best players to transfer in\n4) View worst performing players on your squad\n5) View minutes played by your team\n-1) -1 to quit\n"))
while choice != -1:
    if choice == 1:
        option = int(input("\n1) Most recent gameweek\n2) Enter a gameweek\n3) All gameweeks\n"))
        if option == 1:
            for position in initial_team.initial_squad:
                for player in position:
                    name = player[1]
                    print(name, ": ", transfers.player_points_dict[name][-1])
            print("\n")
        elif option == 2:
            userGW = int(input("\nEnter gameweek: \n"))
            for position in initial_team.initial_squad:
                for player in position:
                    name = player[1]
                    print(name, ": ", transfers.player_points_dict[name][userGW-1])
            print("\n")
        elif option == 3:
            i = 1
            while i < gw:
                print("GW", i, "\n")
                for position in initial_team.initial_squad:
                    for player in position:
                        name = player[1]
                        print(name, ": ", transfers.player_points_dict[name][i-1])
                print("\n---------------------------\n")
                i = i+1
    elif choice == 2:
        transfers.weeklyRecs(initial_team.initial_squad)
    elif choice == 3:
        pprint( transfers.findBestPlayers(gw) )
    elif choice == 4:
        gws, squadPoints = transfers.findWorstPlayers(gw, initial_team.initial_squad)
        print("\nYours squads point sum from the last", gws, "gws: ")
        for key,value in squadPoints.items():
            print(key, ":", value)
    elif choice == 5:
        gws, squadMins = transfers.minutesPlayed(gw, initial_team.initial_squad)
        print("\nYours squads minutes played from the last", gws, "gws: ")
        pprint(squadMins)
    choice = int(input( "\n1) View team's points scored\n2) View recommended team\n3) Find best players to transfer in\n4) View worst performing players on your squad\n5) View minutes played by your team\n-1) -1 to quit\n"))


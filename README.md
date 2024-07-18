# fpl_points_predictor

Using machine learning to create a point predictor for fantasy premier league.

Grouped datasets into positions( GK, DEF, MID, FWD ) and used a random forest model to predict a players points for an upcoming gameweek.  Features considered include total goals, assists, clean sheets, expected stats, bonus points system, etc. recorded for all prior weeks leading up to the current gameweek.

I used data from the 2023/2024 season as my test dataset, and the three previous seasons as my training dataset.

Data from https://github.com/vaastav/Fantasy-Premier-League.

# fpl_points_predictor

Using machine learning to create a point predictor for Fantasy Premier League( https://fantasy.premierleague.com/ ).

Used a random forest model to predict players' points for an upcoming gameweek.  Features include stats such as total goals, assists, clean sheets, expected stats, and bonus points system.  Different features were used for the different positions( GK, DEF, MID, FWD ).

I used data from the 2023/2024 season as my test dataset, and the three previous seasons as my training dataset.

Included functions to pick the best squad considering budget, and which players to start based on predicted points.

Data from https://github.com/vaastav/Fantasy-Premier-League.

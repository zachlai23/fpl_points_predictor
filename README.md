# fpl_points_predictor
Using machine learning to create a point predictor for Fantasy Premier League(https://fantasy.premierleague.com/). 

## Model Details
### Datasets
- **Training Data:** 20/21, 21/22, 22/23 season data
- **Testing Data:** 23/24 season data

Data from https://github.com/vaastav/Fantasy-Premier-League.
- **Preprocessing:** data from each player is averaged across prior gameweeks and then used as features for the model.
  - Features considered vary by position but include goals scored, assists, clean sheets, expected points/goals/assists/clean sheets/goals conceded, ict_index, bps,...
### Random Forest Model 
- From scikit learn, outperformed linear regression and neural network models when tested.

## Additional Features
- **Automated Team Management:** Recommends an initial team, and transfers based on predicted points from the model, and analysis of fixtures in the near future.

## Future Improvements
Continue to improve the transfer recommendations taking more details into account.  I plan to create an interactive web application where recommendations can be provided to assists users with their team decisions.

## Example
Recommendations for a given gameweek:

<img width="448" alt="Screenshot 2024-10-05 at 12 41 41 PM" src="https://github.com/user-attachments/assets/a6e985b9-d308-4fff-81a1-4d59a6d30d52">




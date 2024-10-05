# fpl_points_predictor
Using machine learning to create a point predictor for [Fantasy Premier League](https://fantasy.premierleague.com/). 

## Model Details
### Datasets
- **Training Data:** Data from the 20/21, 21/22, 22/23 seasons.
- **Testing Data:** Data from the 23/24 season.

Data from https://github.com/vaastav/Fantasy-Premier-League.
- **Preprocessing:** data from each player is averaged across prior gameweeks and then used as features for the model.
  - Features vary by position and include metrics such as goals scored, assists, clean sheets, expected stats, ict_index, BPS(bonus points system), and more
    
### Random Forest Model 
- From scikit learn, outperformed linear regression and neural network models when tested on historical data.
- A separate model was created for each position(Goalkeeper, Defender, Midfielder, Forward), which significantly improved accuracy compared to using a single model for all positions.
- Provides insight into which metrics matter most for each position.

## Additional Features
- **Automated Team Management:** Recommends an initial team under the given budget, and proposes transfers based on predicted points from the model.  It also takes into account actual points scored from prior weeks and upcoming fixture difficulty.

## Future Improvements
**Motivation:** I am interested in exploring how computer models based on statistical analysic compare to hand picked teams by human managers.  i hope to get this project to the point where it outperforms my hand picked team. 

Future work will focus on improving transfer recommendations by considering additional factors.  I also plan to develop an interactive web application to provide users with customized team suggestions.

## Example
Recommendations for a given gameweek:

<img width="448" alt="Screenshot 2024-10-05 at 12 41 41 PM" src="https://github.com/user-attachments/assets/a6e985b9-d308-4fff-81a1-4d59a6d30d52">




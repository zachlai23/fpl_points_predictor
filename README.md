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
- **Interactive Input/Output:** Allows users to request different recommendations for their team.

## Future Improvements
**Motivation:** I am interested in exploring how computer models based on statistical analysic compare to hand picked teams by human managers.  I hope to progress this project to the point where it consistently outperforms many hand picked teams. 

Future work will focus on improving transfer recommendations by considering additional factors.  I also plan to develop an interactive web application to provide users with customized team suggestions.

## Example
Recommendations for a given gameweek:

<img width="328" alt="Screenshot 2024-10-05 at 1 42 53 PM" src="https://github.com/user-attachments/assets/85408714-fc0b-4f43-ac4f-4dcd609e6a19">

<img width="455" alt="Screenshot 2024-10-05 at 1 42 08 PM" src="https://github.com/user-attachments/assets/0d071111-b1b4-4382-ab6e-c009be5c4caf">

<img width="454" alt="Screenshot 2024-10-05 at 1 42 32 PM" src="https://github.com/user-attachments/assets/369def3a-2ec6-4b6d-9e48-44788a0f0792">

<img width="350" alt="Screenshot 2024-10-05 at 1 42 42 PM" src="https://github.com/user-attachments/assets/29ec48bc-70ec-48a0-8d1b-b5f036957087">




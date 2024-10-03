# Copy of Jupyter Notebook to .py file

# In[41]:
import pandas as pd  # type: ignore
from sklearn.ensemble import RandomForestRegressor  # type: ignore
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score  # type: ignore
from pprint import pprint
from pathlib import Path # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore

pd.options.mode.chained_assignment = None  # default='warn'

# # Datasets

# In[42]:
MERGED_GW = Path('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/mergedGW')
POS_SORTED = Path('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted')

df2 = pd.read_csv(MERGED_GW / '20:21mergedGW.csv')
df3 = pd.read_csv(MERGED_GW / '21:22mergedGW.csv')
df4 = pd.read_csv(MERGED_GW / '22:23mergedGW.csv')
test_df = pd.read_csv(MERGED_GW / '23:24mergedGW.csv')

df2 = df2.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
df3 = df3.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
df4 = df4.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
test_df = test_df.sort_values( by=['name', 'GW'] ).reset_index( drop=True )

# In[43]:

# Save prices of each player for after the predictions
price_df = test_df[['name','team','position','GW','value']]
price_df['value'] = price_df['value']/10
price_df = price_df.drop_duplicates(subset=['name', 'GW'], keep='first')    

# In[44]:

# Combine data from 20/21, 21/22, 22/23 seasons for the training set
dataframes = [ df2, df3, df4 ]
df = pd.concat( dataframes, ignore_index = True )

# In[45]:

# Sort by positions for training set
gk_df = df[df['position'] == 'GK']
def_df = df[df['position'] == 'DEF']
mid_df = df[df['position'] == 'MID']
fwd_df = df[df['position'] == 'FWD']

# In[46]:

# Sort by positions for test set
gk_test_df = test_df[test_df['position'] == 'GK']
def_test_df = test_df[test_df['position'] == 'DEF']
mid_test_df = test_df[test_df['position'] == 'MID']
fwd_test_df = test_df[test_df['position'] == 'FWD']

# In[47]:

# Create a mapping from player names to categorical codes
def name_mapping( df ):
    df['name'] = df['name'].astype('category')
    name_mapping = dict(enumerate( df['name'].cat.categories ) )
    name_mapping_reverse = { v: k for k, v in name_mapping.items() }
    df['name'] = df['name'].cat.codes
    return df, name_mapping, name_mapping_reverse

# In[48]:

team_strength = { 1:5, 2:3, 3:3, 4:3, 5:3, 6:3, 7:3, 8:3, 9:3, 10:2, 11:2, 12:4, 13:5, 14:3, 15:4, 16:3, 17:2, 18:3, 19:3, 20:3 }

def print_results( actual, predicted ):
    print( 'mean squared error: ', mean_squared_error( actual, predicted ) )
    print( 'mean absolute error: ', mean_absolute_error( actual, predicted ) )
    print( 'r2 score: ', r2_score( actual, predicted ) )


# Splits the dataframe into features (X) and the target (y).
def split_features(df, target_column):
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return X, y

# Display a bar chart of feature importance for given model
def display_feature_importance(model, feature_names):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]  # Sort features by importance
    
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importance")
    plt.bar(range(len(importance)), importance[indices], align="center")
    plt.xticks(range(len(importance)), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.show()

# In[49]:

# Create one function to preprocess data given the dataset and position
def position_preprocess( df, position ):
    # Average or sum statistics to feed to model
    df['avg_ict'] = df.groupby('name')['ict_index'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    df['avg_bps'] = df.groupby('name')['bps'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    df['avg_xP'] = df.groupby('name')['xP'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    df['total_starts'] = df.groupby('name')['starts'].cumsum().shift(1).fillna(0)
    df['avg_mins'] = df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)

    df['was_home'] = df['was_home'].astype('category')
    df['was_home'] = df['was_home'].cat.codes

    # Create a value dataset for prices and return
    df['value'] = df['value']/10
    value = df[['name','team','GW','value']]

    df['opponent_strength'] = df['opponent_team'].map(team_strength)

    # Edit features specific to position
    if position == 'gk':
        df['avg_saves'] = df.groupby('name')['saves'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_pen_saves'] = df.groupby('name')['penalties_saved'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_goals_conceded'] = df.groupby('name')['goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_cs'] = df.groupby('name')['clean_sheets'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_x_goals_conceded'] = df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['total_cs'] = df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)

        columns_to_zero = ['avg_saves', 'avg_ict', 'avg_pen_saves','avg_goals_conceded',
                           'avg_xP','avg_cs','avg_bps','avg_mins','avg_x_goals_conceded',
                           'total_starts']
    elif position == 'def':
        df['avg_xA'] = df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xGI'] = df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xGC'] = df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_GC'] = df.groupby('name')['goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_mins'] = df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['total_assists'] = df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
        df['total_goals'] = df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)
        df['total_cs'] = df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)

        columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_GC','avg_xP',
                           'avg_xGI','avg_mins','avg_xGC','total_starts','total_cs',
                           'total_goals','total_assists']
    elif position == 'mid':
        df['avg_xA'] = df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xG'] = df.groupby('name')['expected_goals'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xGI'] = df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xGC'] = df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_GC'] = df.groupby('name')['goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_mins'] = df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['total_assists'] = df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
        df['total_goals'] = df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)
        df['total_cs'] = df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)

        columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_GC','avg_xP',
                           'avg_xG','avg_xGI','avg_mins','avg_xGC','total_starts',
                           'total_cs','total_goals','total_assists']
    elif position == 'fwd':
        df['avg_xA'] = df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xG'] = df.groupby('name')['expected_goals'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_xGI'] = df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['avg_mins'] = df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
        df['total_assists'] = df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
        df['total_goals'] = df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)

        columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_xG','avg_xP','avg_xGI',
                           'avg_mins','total_starts','total_goals','total_assists']

    df = df.drop(['opponent_team', 'value', 'position', 'team', 'starts', 'transfers_balance',
                    'bonus', 'own_goals', 'saves', 'round', 'team_a_score', 'team_h_score', 'yellow_cards',
                    'red_cards', 'bps', 'transfers_in', 'transfers_out', 'penalties_missed', 'penalties_saved',
                    'clean_sheets', 'element', 'selected', 'ict_index', 'assists', 'goals_scored', 'creativity',
                    'influence', 'threat', 'xP', 'kickoff_time', 'fixture', 'expected_assists', 'expected_goals',
                    'expected_goal_involvements', 'goals_conceded', 'expected_goals_conceded', 
                    'minutes'], axis=1)

    df.loc[df['GW'] == 1, columns_to_zero] = 0
        
    return df, value
# In[50]:

gk_df = pd.read_csv( POS_SORTED / 'goalkeepers.csv')
gk_df, gk_name_mapping, gk_name_mapping_reverse = name_mapping( gk_df )
gk_df, gk_value = position_preprocess( gk_df, 'gk' )

gk_test_df = pd.read_csv(POS_SORTED / 'goalkeepers_test.csv')
gk_test_df, gk_test_name_mapping, gk_test_name_mapping_reverse = name_mapping( gk_test_df )
gk_test_df, gk_test_value = position_preprocess( gk_test_df, 'gk' )

# In[51]:

# Split training and testing datasets
gk_X_train, gk_y_train = split_features(gk_df, 'total_points')
gk_X_test, gk_y_test = split_features(gk_test_df, 'total_points')
gk_X_test = gk_X_test.drop(columns=['Unnamed: 0'])

# ### Random Forest

# In[53]:

gk_rf = RandomForestRegressor( max_depth=4, max_features= 15, n_estimators= 500, random_state=13 ) # max depth helps avoid overfitting, max features helps accuracy
gk_rf.fit( gk_X_train, gk_y_train )

# In[54]:

gk_train_pred = gk_rf.predict( gk_X_train )
gk_pred = gk_rf.predict( gk_X_test )


# # Defenders

# In[57]:

def_df = pd.read_csv(POS_SORTED / 'defenders.csv')
def_df, def_name_mapping, def_name_mapping_reverse = name_mapping( def_df )
def_df,def_value = position_preprocess( def_df, 'def' )

def_test_df = pd.read_csv(POS_SORTED / 'defenders_test.csv')
def_test_df, def_test_name_mapping, def_test_name_mapping_reverse = name_mapping( def_test_df )
def_test_df,def_test_value = position_preprocess( def_test_df, 'def' )

# In[58]:

# Split training and testing datasets
def_X_train, def_y_train = split_features(def_df, 'total_points')
def_X_test, def_y_test = split_features(def_test_df, 'total_points')
def_X_test = def_X_test.drop(columns=['Unnamed: 0'])

# ### Random Forest
# In[60]:

def_rf = RandomForestRegressor( max_depth=4,max_features= 5,n_estimators= 500,random_state=13 )
def_rf.fit( def_X_train, def_y_train )

# In[61]:

def_train_pred = def_rf.predict( def_X_train )
def_pred = def_rf.predict( def_X_test )


# # Midfielders
# # In[64]:

mid_df = pd.read_csv(POS_SORTED / 'midfielders.csv')
mid_df, mid_name_mapping, mid_name_mapping_reverse = name_mapping( mid_df )
mid_df, mid_value = position_preprocess( mid_df, 'mid' )

mid_test_df = pd.read_csv(POS_SORTED / 'midfielders_test.csv')
mid_test_df, mid_test_name_mapping, mid_test_name_mapping_reverse = name_mapping( mid_test_df )
mid_test_df, mid_test_value = position_preprocess( mid_test_df, 'mid' )

# In[65]:
# Split training and testing datasets
mid_X_train, mid_y_train = split_features(mid_df, 'total_points')
mid_X_test, mid_y_test = split_features(mid_test_df, 'total_points')
mid_X_test = mid_X_test.drop(columns=['Unnamed: 0'])

# In[67]:

mid_rf = RandomForestRegressor( max_depth=4,max_features= 10,n_estimators= 100,random_state=13 )
mid_rf.fit( mid_X_train, mid_y_train )

# In[68]:

mid_train_pred = mid_rf.predict( mid_X_train )
mid_pred = mid_rf.predict( mid_X_test )


# # Forwards
# In[71]:

fwd_df = pd.read_csv(POS_SORTED / 'forwards.csv')
fwd_df, fwd_name_mapping, fwd_name_mapping_reverse = name_mapping( fwd_df )
fwd_df, fwd_value = position_preprocess( fwd_df, 'fwd' )

fwd_test_df = pd.read_csv(POS_SORTED / 'forwards_test.csv')
fwd_test_df, fwd_test_name_mapping, fwd_test_name_mapping_reverse = name_mapping( fwd_test_df )
fwd_test_df, fwd_test_value = position_preprocess( fwd_test_df, 'fwd' )

# In[72]:
# Split training and testing datasets
fwd_X_train, fwd_y_train = split_features(fwd_df, 'total_points')
fwd_X_test, fwd_y_test = split_features(fwd_test_df, 'total_points')
fwd_X_test = fwd_X_test.drop(columns=['Unnamed: 0'])

# In[74]:

fwd_rf = RandomForestRegressor( max_depth=4,max_features= 10,n_estimators= 100,random_state=13 )
fwd_rf.fit( fwd_X_train, fwd_y_train )

# In[75]:

fwd_train_pred = fwd_rf.predict( fwd_X_train )
fwd_pred = fwd_rf.predict( fwd_X_test )

# Output results and feature importance charts
if __name__ == "__main__":
    print(def_X_test.columns)
    print( "GK results:")
    print_results( gk_y_test, gk_pred )
    print('-------------------------------')
    print_results( gk_y_train, gk_train_pred )

    print("\nDEF results:")
    print_results( def_y_test, def_pred )
    print('-------------------------------')
    print_results( def_y_train, def_train_pred )

    print("\nMID results:")
    print_results( mid_y_test, mid_pred )
    print('-------------------------------')
    print_results( mid_y_train, mid_train_pred )

    print("\nFWD results:")
    print_results( fwd_y_test, fwd_pred )
    print('-------------------------------')
    print_results( fwd_y_train, fwd_train_pred ) 

    display_feature_importance( gk_rf, gk_X_test.columns)  
    display_feature_importance( def_rf, def_X_test.columns)  
    display_feature_importance( mid_rf, mid_X_test.columns)  
    display_feature_importance( fwd_rf, fwd_X_test.columns)  
# Copy of Jupyter Notebook to script

# In[41]:


import pandas as pd  # type: ignore
from sklearn.ensemble import RandomForestRegressor  # type: ignore
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score  # type: ignore
from pprint import pprint
pd.set_option('future.no_silent_downcasting', True)
pd.options.mode.chained_assignment = None  # default='warn'


# # Datasets

# In[42]:


df2 = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/mergedGW/20:21mergedGW.csv')
df3 = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/mergedGW/21:22mergedGW.csv')
df4 = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/mergedGW/22:23mergedGW.csv')
test_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/mergedGW/23:24mergedGW.csv')

df2 = df2.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
df3 = df3.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
df4 = df4.sort_values( by=['name', 'GW'] ).reset_index( drop=True )
test_df = test_df.sort_values( by=['name', 'GW'] ).reset_index( drop=True )


# In[43]:


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


team_strength = { 1:5, 2:4, 3:3, 4:3, 5:3, 6:2, 7:3, 8:3, 9:3, 10:3, 11:4, 12:2, 13:5, 14:3, 15:3, 16:3, 17:2, 18:4, 19:3, 20:3 }

def print_results( actual, predicted ):
    print( 'mean squared error: ', mean_squared_error( actual, predicted ) )
    print( 'mean absolute error: ', mean_absolute_error( actual, predicted ) )
    print( 'r2 score: ', r2_score( actual, predicted ) )

# # Goalkeepers

# ### Data Preprocessing

# In[49]:


def gk_preprocess( gk_df ):
    gk_df['avg_saves'] = gk_df.groupby('name')['saves'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_ict'] = gk_df.groupby('name')['ict_index'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_pen_saves'] = gk_df.groupby('name')['penalties_saved'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_goals_conceded'] = gk_df.groupby('name')['goals_conceded'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_xP'] = gk_df.groupby('name')['xP'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_cs'] = gk_df.groupby('name')['clean_sheets'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_bps'] = gk_df.groupby('name')['bps'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_mins'] = gk_df.groupby('name')['minutes'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    gk_df['avg_x_goals_conceded'] = gk_df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).reset_index(level=0, drop=True)
    
    gk_df['total_pen_saves'] = gk_df.groupby('name')['penalties_saved'].cumsum().shift(1).fillna(0)
    gk_df['total_cs'] = gk_df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)
    gk_df['total_starts'] = gk_df.groupby('name')['starts'].cumsum().shift(1).fillna(0)

    gk_df['team'] = gk_df['team'].astype('category')
    gk_df['team'] = gk_df['team'].cat.codes
        
    gk_df['was_home'] = gk_df['was_home'].astype('category')
    gk_df['was_home'] = gk_df['was_home'].cat.codes

    gk_df['value'] = gk_df['value']/10
    gk_value = gk_df[['name','team','GW','value']]
        
    gk_df = gk_df.fillna(0)

    gk_df['opponent_strength'] = gk_df['opponent_team'].map(team_strength)
        
    gk_df = gk_df.drop(['opponent_team','value','position','total_pen_saves','was_home','team','expected_goals_conceded','penalties_saved','bonus','own_goals','minutes','saves','kickoff_time','team_a_score','team_h_score','expected_assists','expected_goal_involvements','expected_goals','transfers_in','transfers_out','transfers_balance','fixture','assists','goals_scored','ict_index','influence','creativity','threat','penalties_missed','selected','goals_conceded','xP','clean_sheets','element','round','red_cards','yellow_cards','starts','bps','total_pen_saves','total_cs'],axis=1)

    columns_to_zero = ['avg_saves', 'avg_ict', 'avg_pen_saves','avg_goals_conceded','avg_xP','avg_cs','avg_bps','avg_mins','avg_x_goals_conceded','total_starts']

    gk_df.loc[gk_df['GW'] == 1, columns_to_zero] = 0
    
    return gk_df, gk_value


# In[50]:


gk_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/goalkeepers.csv')
gk_df, gk_name_mapping, gk_name_mapping_reverse = name_mapping( gk_df )
gk_df, gk_value = gk_preprocess( gk_df )

gk_test_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/goalkeepers_test.csv')
gk_test_df, gk_test_name_mapping, gk_test_name_mapping_reverse = name_mapping( gk_test_df )
gk_test_df, gk_test_value = gk_preprocess( gk_test_df )


# In[51]:


# Split training set
gk_y_train = gk_df['total_points']
gk_X_train = gk_df.drop( ['total_points'], axis=1 )


# In[52]:


# Split test set
gk_y_test = gk_test_df['total_points']
gk_X_test = gk_test_df.drop(['Unnamed: 0','total_points'],axis=1)


# ### Random Forest

# In[53]:


gk_rf = RandomForestRegressor( max_depth=4, max_features= 15, n_estimators= 500, random_state=13 ) # max depth helps avoid overfitting, max features helps accuracy
gk_rf.fit( gk_X_train, gk_y_train )


# In[54]:


gk_train_pred = gk_rf.predict( gk_X_train )

gk_pred = gk_rf.predict( gk_X_test )




# # Defenders

# ### Data Preprocessing

# In[56]:


def def_preprocess( def_df ):
    def_df['avg_ict'] = def_df.groupby('name')['ict_index'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_bps'] = def_df.groupby('name')['bps'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_xP'] = def_df.groupby('name')['xP'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_xA'] = def_df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_xGI'] = def_df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_xGC'] = def_df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_GC'] = def_df.groupby('name')['goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['avg_mins'] = def_df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    def_df['total_assists'] = def_df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
    def_df['total_goals'] = def_df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)
    def_df['total_cs'] = def_df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)
    def_df['total_starts'] = def_df.groupby('name')['starts'].cumsum().shift(1).fillna(0)

    def_df['was_home'] = def_df['was_home'].astype('category')
    def_df['was_home'] = def_df['was_home'].cat.codes

    def_df['value'] = def_df['value']/10
    def_value = def_df[['name','team','GW','value']]

    def_df['opponent_strength'] = def_df['opponent_team'].map(team_strength)

    columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_GC','avg_xP','avg_xGI','avg_mins','avg_xGC','total_starts','total_cs','total_goals','total_assists']

    def_df.loc[def_df['GW'] == 1, columns_to_zero] = 0
    

    def_df = def_df.drop(['opponent_team','value','position','team','starts','minutes','goals_conceded','red_cards','team_a_score','team_h_score','yellow_cards','element','assists','goals_scored','clean_sheets','penalties_missed','penalties_saved','influence','threat','round','saves','selected','threat','kickoff_time','own_goals','fixture','creativity','transfers_balance','transfers_in','transfers_out','ict_index','bps','bonus','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded'],axis=1)
    return def_df, def_value


# In[57]:


def_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/defenders.csv')
def_df, def_name_mapping, def_name_mapping_reverse = name_mapping( def_df )
def_df,def_value = def_preprocess( def_df )

def_test_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/defenders_test.csv')
def_test_df, def_test_name_mapping, def_test_name_mapping_reverse = name_mapping( def_test_df )
def_test_df,def_test_value = def_preprocess( def_test_df )


# In[58]:


def_y_train = def_df['total_points']
def_X_train = def_df.drop( ['total_points'], axis=1 )


# In[59]:


def_y_test = def_test_df['total_points']
def_X_test = def_test_df.drop( ['Unnamed: 0','total_points'], axis=1 )


# ### Random Forest

# In[60]:


def_rf = RandomForestRegressor( max_depth=4,max_features= 5,n_estimators= 500,random_state=13 )
def_rf.fit( def_X_train, def_y_train )


# In[61]:


def_train_pred = def_rf.predict( def_X_train )

def_pred = def_rf.predict( def_X_test )



# # Midfielders

# ### Data Preprocessing

# In[63]:


def mid_preprocess( mid_df ):
    mid_df['avg_ict'] = mid_df.groupby('name')['ict_index'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_assists'] = mid_df.groupby('name')['assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_goals'] = mid_df.groupby('name')['goals_scored'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_bps'] = mid_df.groupby('name')['bps'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_xP'] = mid_df.groupby('name')['xP'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_xA'] = mid_df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_xG'] = mid_df.groupby('name')['expected_goals'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_xGI'] = mid_df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_xGC'] = mid_df.groupby('name')['expected_goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_GC'] = mid_df.groupby('name')['goals_conceded'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['avg_mins'] = mid_df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    mid_df['total_assists'] = mid_df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
    mid_df['total_goals'] = mid_df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)
    mid_df['total_cs'] = mid_df.groupby('name')['clean_sheets'].cumsum().shift(1).fillna(0)
    mid_df['total_starts'] = mid_df.groupby('name')['starts'].cumsum().shift(1).fillna(0)

    mid_df['was_home'] = mid_df['was_home'].astype('category')
    mid_df['was_home'] = mid_df['was_home'].cat.codes

    mid_df['value'] = mid_df['value']/10
    mid_value = mid_df[['name','team','GW','value']]

    mid_df['opponent_strength'] = mid_df['opponent_team'].map(team_strength)

    columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_GC','avg_xP','avg_xG','avg_xGI','avg_mins','avg_xGC','total_starts','total_cs','total_goals','total_assists']

    mid_df.loc[mid_df['GW'] == 1, columns_to_zero] = 0

    mid_df = mid_df.drop(['opponent_team','value','position','team','transfers_balance','bonus','own_goals','saves','team_a_score','team_h_score','red_cards','yellow_cards','transfers_in','transfers_out','penalties_missed','penalties_saved','clean_sheets','creativity','influence','threat','kickoff_time','fixture','round','element','starts','selected','ict_index','assists','avg_assists','goals_scored','avg_goals','bps','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded','goals_conceded','minutes'],axis=1)
    return mid_df, mid_value


# In[64]:


mid_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/midfielders.csv')
mid_df, mid_name_mapping, mid_name_mapping_reverse = name_mapping( mid_df )
mid_df, mid_value = mid_preprocess( mid_df )

mid_test_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/midfielders_test.csv')
mid_test_df, mid_test_name_mapping, mid_test_name_mapping_reverse = name_mapping( mid_test_df )
mid_test_df, mid_test_value = mid_preprocess( mid_test_df )


# In[65]:


mid_y_train = mid_df['total_points']
mid_X_train = mid_df.drop( ['total_points'], axis=1 )


# In[66]:


mid_y_test = mid_test_df['total_points']
mid_X_test = mid_test_df.drop( ['Unnamed: 0','total_points'], axis=1 )


# ### Random Forest

# In[67]:


mid_rf = RandomForestRegressor( max_depth=4,max_features= 10,n_estimators= 100,random_state=13 )
mid_rf.fit( mid_X_train, mid_y_train )


# In[68]:


mid_train_pred = mid_rf.predict( mid_X_train )
mid_pred = mid_rf.predict( mid_X_test )


# # Forwards

# ### Data Preprocessing

# In[70]:


def fwd_preprocess( fwd_df ):
    fwd_df['avg_ict'] = fwd_df.groupby('name')['ict_index'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_assists'] = fwd_df.groupby('name')['assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_goals'] = fwd_df.groupby('name')['goals_scored'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_bps'] = fwd_df.groupby('name')['bps'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_xP'] = fwd_df.groupby('name')['xP'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_xA'] = fwd_df.groupby('name')['expected_assists'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_xG'] = fwd_df.groupby('name')['expected_goals'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_xGI'] = fwd_df.groupby('name')['expected_goal_involvements'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['avg_mins'] = fwd_df.groupby('name')['minutes'].expanding().mean().shift(1).fillna(0).reset_index(level=0, drop=True)
    fwd_df['total_assists'] = fwd_df.groupby('name')['assists'].cumsum().shift(1).fillna(0)
    fwd_df['total_goals'] = fwd_df.groupby('name')['goals_scored'].cumsum().shift(1).fillna(0)
    fwd_df['total_starts'] = fwd_df.groupby('name')['starts'].cumsum().shift(1).fillna(0)
    
    fwd_df['was_home'] = fwd_df['was_home'].astype('category')
    fwd_df['was_home'] = fwd_df['was_home'].cat.codes

    fwd_df['value'] = fwd_df['value']/10
    fwd_value = fwd_df[['name','team','GW','value']]

    fwd_df['opponent_strength'] = fwd_df['opponent_team'].map(team_strength)

    columns_to_zero = ['avg_bps', 'avg_ict', 'avg_xA','avg_xG','avg_xP','avg_xGI','avg_mins','total_starts','total_goals','total_assists']

    fwd_df.loc[fwd_df['GW'] == 1, columns_to_zero] = 0
    
    fwd_df = fwd_df.drop(['opponent_team','value','position','team','transfers_balance','bonus','own_goals','saves','team_a_score','team_h_score','red_cards','yellow_cards','transfers_in','transfers_out','penalties_missed','penalties_saved','clean_sheets','creativity','influence','threat','kickoff_time','fixture','round','element','starts','selected','ict_index','assists','avg_assists','goals_scored','avg_goals','bps','xP','expected_assists','expected_goals','expected_goal_involvements','expected_goals_conceded','goals_conceded','minutes'],axis=1)
    
    return fwd_df, fwd_value


# In[71]:


fwd_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/forwards.csv')
fwd_df, fwd_name_mapping, fwd_name_mapping_reverse = name_mapping( fwd_df )
fwd_df, fwd_value = fwd_preprocess( fwd_df )

fwd_test_df = pd.read_csv('/Users/zacharylai/Desktop/fpl_points_predictor/datasets/position_sorted/forwards_test.csv')
fwd_test_df, fwd_test_name_mapping, fwd_test_name_mapping_reverse = name_mapping( fwd_test_df )
fwd_test_df, fwd_test_value = fwd_preprocess( fwd_test_df )


# In[72]:


fwd_y_train = fwd_df['total_points']
fwd_X_train = fwd_df.drop( ['total_points'], axis=1 )


# In[73]:


fwd_y_test = fwd_test_df['total_points']
fwd_X_test = fwd_test_df.drop( ['Unnamed: 0','total_points'],axis=1 )


# ### Random Forest

# In[74]:


fwd_rf = RandomForestRegressor( max_depth=4,max_features= 10,n_estimators= 100,random_state=13 )
fwd_rf.fit( fwd_X_train, fwd_y_train )


# In[75]:


fwd_train_pred = fwd_rf.predict( fwd_X_train )
fwd_pred = fwd_rf.predict( fwd_X_test )


if __name__ == "__main__":
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
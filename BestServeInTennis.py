# Tennis Men's Singles ATP "Who has the best aces?"
import pandas as pd
import numpy as np

dirname = 'C:\\Users\\Me\\Documents\\GitHub\\tennis_stats_atp\\'
year = '2014'
Surf = 'Grass'
cut_off = 0.0

df = pd.read_csv(dirname+'atp_matches_'+year+'.csv')
# drop unimportant columns
df = df[['surface', 'winner_name', 'loser_name', 'w_ace', 'l_ace', 'w_1stIn', 'l_1stWon','l_1stIn', 'l_1stWon','w_SvGms', 'l_SvGms']]
# select only grass courts
df = df[df['surface'].isin([Surf])]
df = df.drop('surface', 1)
# only take finite values (ignore NaN)
df = df.dropna() 

# calculate aver ace/game
df['w_avgAGm'] = 1.0*df['w_ace']/df['w_SvGms']
df['l_avgAGm'] = 1.0*df['l_ace']/df['l_SvGms']

# split into winners and losers seperatly, then combine into one dataframe
w_df = df[['winner_name', 'w_avgAGm']]
w_df.columns = ['name', 'avgAGm'] # rename columns
l_df = df[['loser_name', 'l_avgAGm']]
l_df.columns = ['name', 'avgAGm'] # rename columns
simple_df = pd.concat([w_df, l_df])

# Simply "who has the highers (unweighted) number of aces/game
grouped = simple_df.groupby('name')
A = grouped.mean().sort(['avgAGm'])
print "Simple analysis of the most aces on "+Surf+" courts."
print A.tail()

# a more complicated weighting using a player/player matrix
df2 = df[['winner_name', 'loser_name', 'l_avgAGm']]
gdf = df2.groupby(['winner_name', 'loser_name'], as_index=False).aggregate(np.mean)
norms = gdf.groupby(['winner_name'], as_index=False).aggregate(np.mean)
# rename norm
norms.rename(columns={'winner_name': 'name', 'l_avgAGm': 'N'}, inplace=True)
#exclude singular terms
norms = norms[norms['N'] > cut_off].sort('N')

df3 = df[['winner_name', 'loser_name', 'w_avgAGm']]
acedf = df3.groupby(['winner_name', 'loser_name'], as_index=False).aggregate(np.mean)
acedf.rename(columns={'loser_name': 'name'}, inplace=True)
# Join the two things
norms = norms.set_index('name')
master_df = acedf.join(norms, on='name')
master_df = master_df.dropna() 
#remove nans

master_df['weight']  = 1.0*(master_df['w_avgAGm']-master_df['N'])
master_df = master_df[['winner_name', 'weight']]
master_df.rename(columns={'weight': 'ace_score'}, inplace=True)
master_df = master_df.groupby(['winner_name'], as_index=False).aggregate(np.sum)

master_df = master_df.sort('ace_score')
#print norms.loc['Roger Federer']
print master_df

#plotting the data
import matplotlib.pyplot as plt
master_df = master_df.set_index('winner_name')
master_df.plot(kind = 'bar', legend=False, title = "Ace Score of ATP Men's Singles Players in "+year)
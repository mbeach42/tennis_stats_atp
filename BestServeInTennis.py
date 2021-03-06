# Tennis Men's Singles ATP "Who has the best aces?"

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
    
dirname = 'C:\\Users\\Me\\Documents\\GitHub\\tennis_stats_atp\\'
year = '2014'
Surf = 'All'

# import data, only take important columns, and drop missing data
def readData(year, Surf):
    df = pd.read_csv(dirname+'atp_matches_'+year+'.csv')
    df = df[['surface', 'winner_name', 'loser_name', 'w_ace', 'l_ace', 'w_1stIn', 'l_1stWon','l_1stIn', 'l_1stWon','w_SvGms', 'l_SvGms']]
    if Surf != 'All':
        df = df[df['surface'].isin([Surf])]
    df = df.drop('surface', 1)
    df = df.dropna() 
    return df

# average number of aces per game
def avgAcePerGm(df):
    df['w_avgAGm'] = 1.0*df['w_ace']/df['w_SvGms']
    df['l_avgAGm'] = 1.0*df['l_ace']/df['l_SvGms']
    return df
    
def unweightedScore(df):
    # split into winners and losers seperatly, then combine into one dataframe
    w_df = df[['winner_name', 'w_avgAGm']]
    w_df.columns = ['name', 'avgAGm'] # rename columns
    l_df = df[['loser_name', 'l_avgAGm']]
    l_df.columns = ['name', 'avgAGm'] # rename columns
    simple_df = pd.concat([w_df, l_df])  
    # Simply "who has the highers (unweighted) number of aces/game
    score_df = simple_df.groupby('name').mean().sort(['avgAGm'], ascending=False)
    return score_df


# More advanced functions
def normalizePlayers(df):
    gdf = df[['winner_name', 'loser_name', 'l_avgAGm']] \
        .groupby(['winner_name', 'loser_name'], as_index=False) \
        .mean()
    norms = gdf.groupby(['winner_name'], as_index=False).mean()
    norms.rename(columns={'winner_name': 'name', 'l_avgAGm': 'N'}, inplace=True)
    norms = norms.set_index('name')
    norms = norms.dropna() 
    return norms

def acesDF(df):
    ace_df = df[['winner_name', 'loser_name', 'w_avgAGm']] \
        .groupby(['winner_name', 'loser_name'], as_index=False) \
        .mean()
    ace_df.rename(columns={'loser_name': 'name'}, inplace=True)
    # Join the norms and scores_df
    norms = normalizePlayers(df)
    joined_df = ace_df.join(norms, on='name')
    joined_df = joined_df.dropna() 
    return joined_df
    
def weightedScore(aces_df):
    scores_df = aces_df
    scores_df['ace_score']  = 1.0*(aces_df['w_avgAGm'] - aces_df['N'])/aces_df['N']
    scores_df_mean = scores_df[['winner_name', 'ace_score']] \
        .groupby(['winner_name']) \
        .mean()
    scores_df_std = scores_df[['winner_name', 'ace_score']] \
        .groupby(['winner_name']) \
        .std()
    scores_df = scores_df_mean
    scores_df['std'] = scores_df_std['ace_score']
    scores_df = scores_df.replace([np.inf, -np.inf], np.nan).dropna()
    scores_df = scores_df.sort('ace_score', ascending=False)
    scores_df.rename(columns={'winner_name': 'name'}, inplace=True)
    return scores_df

def plotTopN(df, N):
    top_df = df.head(N)
    top_df['ace_score'].plot(kind = 'bar', 
        yerr=top_df[['std']].values.T,
        legend=False,
        title = "Ace Score of ATP Men's Singles Players in "+year+" on "+Surf)
    plt.grid(b = False)
    plt.xlabel('Player')
    plt.ylabel('Ace Score')
    plt.savefig('figures\\'+year+'_'+Surf+'.png')

def avgAcesGame(aces_df):
    aces_mean = aces_df['ace_score'].mean()
    return aces_mean
    
# Simple scores
def simpleScores(df):
    df = avgAcePerGm(df)
    simple_df = unweightedScore(df)
    
    print "\nSimple analysis of the most aces on "+Surf+" courts. \n"
    print simple_df.head(10)
    #print simple_df.tail(3)

# Weighted scores
def normalizedScores(df):
    df = avgAcePerGm(df)
    aces_df = acesDF(df)
    scores_df = weightedScore(aces_df)
   
    print "\n Weighted analysis of aces  on "+Surf+" courts.\n"
    print scores_df.head(10)
    #print scores_df.tail(5)
    plotTopN(scores_df, 10)

# To figures out teh best of all time, let's average over may years
def loadMultiYear(year1, year2, Surf):
    df = readData("%d" % (year1), Surf)
    for i in range(year1, year2):
        print "Year %d" % (i)
        df2 = readData("%d" % (i), Surf)
        df = pd.concat([df, df2])
    simpleScores(df)
    normalizedScores(df)
    print '\n The average number of aces per game is' 
    print avgAcesGame(scores_df)
        
# The greatest of all time?
loadMultiYear(2003, 2015, 'All')
# Again this is unnormalized, I should normalize by avgNumAces/Gm per year
# THis is because courts got faster, so more aces


 
#plotTopN(scores_df, 20)
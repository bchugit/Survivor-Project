
import process_votes
import make_graphs
import network
import numpy as np
import pickle
import pandas as pd

def get_season_stats(votes):
    num_episodes = sum(votes.iloc[0, :] != "Jury Vote")
    num_finalists = votes.shape[1] - num_episodes
    jury_votes = votes[votes.columns[-num_finalists:]].fillna('')
    num_jurors = sum(
        [sum( [i.strip() == c for i in jury_votes[c]] ) 
         for c in jury_votes]
    )
    return {'num_episodes':  num_episodes,
            'num_finalists': num_finalists,
            'num_jurors'   : num_jurors}

def votes_correct_against(votes):

    l = len(votes.columns)

    tally = pd.DataFrame(index=[votes.index], columns=['votes_correct', 'votes_against'])
    tally = tally.fillna(0)
    episodes = []
   
    for i in range(0,l):
        
        # Count episode numbers
        episodes.append(i)
        episodes_cumulative = pd.DataFrame(votes[votes.columns[episodes]])
        current = episodes_cumulative[episodes_cumulative.columns[i]]
        
        # TODO: Split / remove vote-overs
        # Current workaround ignores these entire votes
        if len(pd.DataFrame(current).columns) > 1:
            current = pd.Series(str(np.zeros(l)))

        # Remove whitespace in scraped values
        current = current.str.strip()
        
        # Votes correct (voted for eliminated player)
        eliminated = current.name
        vcdf = pd.DataFrame(current, columns=[str(eliminated)])
        try:
            correct_vote = vcdf[vcdf[eliminated] == eliminated].index
        except: 
            correct_vote=[]
        tally.loc[tally.index.isin(correct_vote), ['votes_correct']] = tally['votes_correct'] + 1
        
        # Votes against 
        va = current.value_counts()
        vadf = pd.DataFrame(va, columns=['votes'])
        tally.loc[tally.index.isin(vadf.index), ['votes_against']] = vadf['votes'] + tally['votes_against']

    return tally

def scores_from_votes(votes):
    
    eliminated_players = votes.columns
    
    # Turn vote matrix into graph object
    v = process_votes.compare_votes(votes)
    
    g = make_graphs.make_graph(v)
    
    # Calculate scores
    scores = network.centrality_scores(votes, g)
    
    # Add votes for and against
    vca = votes_correct_against(votes)
    scores = scores.join(vca, on='name')
    
    # Binary classification of winners (1) and losers (0)
    scores['place'] = np.where(scores['place'] == 1, 1, 0)
    
    # Rearrange columns
    scores = scores[['name','deg','close','btw','eig','page','votes_correct','votes_against','place']]
    
    # Filter out eliminated players
    fltr = [i.strip() not in eliminated_players for i in scores['name']]
    
    return scores.loc[fltr, :]

def map_prct_to_episode(prct, num_episodes):
    return int( round(prct * num_episodes, 0) )

def truncate_votes_thru_episode(votes, episode):
    # drop later episodes
    eliminated_players = votes.columns[:episode]
    # eliminating rows causes errors ...
    # rows = votes.index[
    #     [i not in eliminated_players for i in votes.index]]
    # return votes.loc[rows, eliminated_players]
    return votes[eliminated_players]

def process_season(votes, time_line_prct):
    season_stats = get_season_stats(votes)
    season_stats['scores'] = {}
    num_episodes = season_stats['num_episodes']
    for prct in time_line_prct:
        # print prct
        thru_episode = map_prct_to_episode(prct, num_episodes)
        votes_trunc = truncate_votes_thru_episode(
            votes, thru_episode)
        scores = scores_from_votes(votes_trunc)
        season_stats['scores'][prct] = scores
    return season_stats

def process_all_seasons(seasons, time_line_prct, save_to_disk=True):
    for season in seasons.keys():
        print season
        current_season = seasons[season]
        votes = current_season['votes']
        current_season['features'] = process_season(votes, time_line_prct)
    
    if save_to_disk:
        pickle.dump(seasons, open( "episode_scores.p", "wb" ) )
    # no return - mutates seasons
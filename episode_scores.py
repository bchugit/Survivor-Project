
import process_votes
import make_graphs
import network
import numpy as np
import pickle

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
    
def scores_from_votes(votes):
    
    # Turn vote matrix into graph object
    V = process_votes.compare_votes(votes)
    
    G = make_graphs.make_graph(V)
    
    # Calculate scores
    C = network.centrality_scores(votes, G)
    
    # Binary classification of winners (1) and losers (0)
    C['place'] = np.where(C['place'] == 1, 1, 0)
                
    # Return dataframe
    return C

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
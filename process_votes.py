
import pandas as pd
import numpy as np
import pickle
import itertools as iter

def drop_jury_votes(votes):
    vote_filter = votes.columns[votes.iloc[0, :] == "Jury Vote"]
    return votes.drop(vote_filter, 1), sum([not i for i in vote_filter])

# def per_episode_votes(votes_all, prct_num_episodes=[1]):
#     # will generate a votes weighting for each entry in the prct_num_episodes list
#     # e.g. [.5, 1] will generate to data frames
#     #  -- voting weights of remaining contestants at half way through the season
#     #  -- voting weighper_episode_votests of remaining contestants at all the way through the season
#     votes, num_finalists = drop_jury_votes(votes_all)
#     num_episodes = votes.shape[1]
    

def compare_votes(votes_all):
    # Create a contestant by contestant matrix corresponding to the number of like votes
    
    # Drop columns corresponsing to final counsel (these votes are a different dynamic)
    votes = drop_jury_votes(votes_all)[0]
    
    like_votes = np.array([None] * votes.shape[0]**2).reshape((votes.shape[0], votes.shape[0]))

    for (i, j) in iter.combinations(range(votes.shape[0]), 2):
        like_votes[i, j] = sum((votes.iloc[i, :] == votes.iloc[j, :]) & #same vote
                               (votes.iloc[i, :] !=  u' \u2014') & #ignore '-' (didn't vote)
                               (votes.iloc[i, :] !=  None) & # ignore 'None' (didn't vote)
                               (votes.iloc[i, :] != '')) #ignore blanks (already eliminated)

    like_votes = pd.DataFrame(like_votes)
    like_votes.index = votes.index
    like_votes.columns = votes.index
    return like_votes

def get_voteweights(seasons, save_to_disk=True):
    voteweights = {}
    for i in seasons.keys():
        voteweights[i] = compare_votes(seasons[i]['votes'])
    
    if save_to_disk:
        pickle.dump(voteweights, open( "process_votes.p", "wb" ) )
    
    return voteweights
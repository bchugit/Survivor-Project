
# Make network graphs
import pandas as pd
import pickle
import numpy as np
import networkx as nx

def make_graph(votes):
    
    # Create adjacency matrix
    votes = votes.fillna(0) #convert None to zeroes
    votes_matrix = votes.as_matrix() #creates numpy array
    votes_matrix = np.matrix(votes_matrix) #creates matrix

    # Make graph
    G = nx.from_numpy_matrix(votes_matrix)
    
    # Rename nodes
    names = list(votes.columns.values)
    nodeints = list(range(len(names)))
    rename = {}
    for i in nodeints:
        rename[i] = names[i]
    G = nx.relabel_nodes(G, rename)
        
    return G

def make_all_graphs(voteweights, save_to_disk=True):
    graphs = {}
    for i in voteweights.keys():
        graphs[i] = make_graph(voteweights[i])
    
    if save_to_disk:
        pickle.dump(graphs, open( "make_graphs.p", "wb" ) )
    return graphs
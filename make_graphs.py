
# Make network graphs
import pandas as pd
import pickle
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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


def draw_graph(G, vw, weighted=False):
    
    # color nodes differently for top 4 finishers
    top4 = list(vw.columns[:4])
    others = list(vw.columns[4:])
    
    plt.figure(figsize=(15,15))
    pos = nx.spring_layout(G, k=0.9, iterations=15, scale=0.5) 

    # nodes
    nx.draw_networkx_nodes(G, pos, nodelist=top4, node_size=1500, 
                           node_color='yellow', alpha=0.6)
    
    nx.draw_networkx_nodes(G, pos, nodelist=others, node_size=1000, 
                           node_color='lightblue', alpha=0.6)
    
    # edges
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    
    # labels
    if weighted == True:           
        labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    
    nx.draw_networkx_labels(G,pos,font_size=15,font_family='sans-serif')


    plt.axis('off')
    plt.show()
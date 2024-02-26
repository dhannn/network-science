import sys
import networkx as nx
import random
import pandas as pd

from tqdm import tqdm

def fail(G: nx.Graph):
    n = random.choice(list(G.nodes()))
    G.remove_node(n)

def attack_degree(G: nx.Graph):
    degrees = G.degree()
    
    sorted_by_degree = sorted(degrees, key=lambda x: x[1], reverse=True)

    G.remove_node(sorted_by_degree[0][0])

def attack_betweenness(G: nx.Graph):
    betweenness = nx.betweenness_centrality(G)
    max_betweenness = max(betweenness.values())
    max_keys = [ k for k, v in betweenness.items() if v == max_betweenness ]
    G.remove_node(max_keys[0])

def do_experiment(G: nx.Graph, num_removals: int, removal_method='random', measure_every_X_removal: int=20):
    
    sys.stderr.write("---- Starting Experiments ---- \n")
    sys.stderr.flush()

    results = pd.DataFrame(columns=['diameter', 'average_path_length', 'largest_component_size'])

    for x in tqdm(range(num_removals)):

        if removal_method == 'random':
            fail(G)
        else:
            removal_method(G)
        
        if x % measure_every_X_removal == 0:
            stats = report_statistics(G)
            results.loc[x] = stats
    
    sys.stderr.write("---- Experiments Finished ---- \n")
    return results

def report_statistics(G: nx.Graph):
    
    G_cc = __get_connected_components(G)
        
    path_lengths = __get_path_lengths(G_cc[0])
    diameter = max(path_lengths)

    try:
        avg_path_length = sum(path_lengths) / (G_cc[0].order() * (G_cc[0].order() - 1))
    except ZeroDivisionError:
        avg_path_length = 0.0
    
    
    largest_component_percentage = float(G_cc[0].order()) / float(G.order())

    return pd.Series(
        [diameter, avg_path_length, largest_component_percentage],
        ['diameter', 'average_path_length', 'largest_component_size']
    )
     

def __get_path_lengths(G):
    path_lengths = []

    for n in G:
        path_length = nx.single_source_shortest_path_length(G, n).values()
        path_lengths.extend(path_length)
    
    return path_lengths

def __get_connected_components(G: nx.Graph):
    return sorted([G.subgraph(c).copy() for c in nx.connected_components(G)], key=len, reverse=True)


"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:       This file consists of a function that finds all cycles in a 
            preference level of a valid smart profile.
"""

import networkx as nx

def find_cycles(Voting, preference_level):
    """
    Finds all cycles that occur in a preference level.
    returns: all found cycles
    """
    linked = {agent : [] for agent in Voting.agents}

    for i, line in enumerate(Voting.profile[preference_level]):
        for agent in Voting.agents:
            if agent in line and Voting.X[Voting.agents[i]] is None:
                linked[Voting.agents[i]].append(agent)

    g = nx.DiGraph()
    g.add_nodes_from(linked.keys())

    for agent, dependent_agents in linked.items():
        g.add_edges_from(([(agent, linked_agent) for linked_agent in dependent_agents]))

    cycles = nx.simple_cycles(g)
    
    return cycles    
        

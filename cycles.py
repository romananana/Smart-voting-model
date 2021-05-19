import networkx as nx
import matplotlib.pyplot as plt

def find_cycles(Voting, Y, preference_level):
    linked = {agent : [] for agent in Voting.agents}

    for i, line in enumerate(Voting.profile[preference_level]):
        for agent in Voting.agents:
            if agent in line and Y[Voting.agents[i]] is None:
                linked[Voting.agents[i]].append(agent)

    g = nx.DiGraph()
    g.add_nodes_from(linked.keys())

    for agent, dependent_agents in linked.items():
        g.add_edges_from(([(agent, linked_agent) for linked_agent in dependent_agents]))

    cycles = nx.simple_cycles(g)
    
    return cycles    

def cycle_duplicates(cycles, target_cycle):
    for cycle in cycles:
        if set(cycle) != set(target_cycle):
            continue
            
        first_letter = target_cycle[0]
        index = cycle.index(first_letter)

        if (cycle[index:] + cycle[:index]) == tuple(target_cycle):
            return True

    return False
        

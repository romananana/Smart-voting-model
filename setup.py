"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:        
"""

import pandas as pd
import copy
import random
import re
from collections import Counter
import string
import networkx as nx

class SmartVoting:
    def __init__(self, df, agents):
        self.ballot = df       # Delegation ballot
        self.D = ['0', '1']     # Possible outcome
        self.agents = agents

    def reset_outcome(self):
        self.X = {}
        for agent in self.agents:
            self.X[agent] = None

    def calculate_output(self):
        algorithms = ['U', 'DU', 'RU', 'DRU']
        # Calculate result for all of the unravelling procedures
        # for i, func in enumerate([self.update_u]):
        for i, func in enumerate([self.update_u, self.update_du, self.update_ru, self.update_dru]):
            self.reset_outcome()
            all_cycles = set()
            while None in self.X.values():
                level = 1
                Y = copy.deepcopy(self.X)
                while Y == self.X:
                    for cycle in self.count_cycles(Y, level):
                        all_cycles.add(tuple(cycle))
                    self.X = func(Y, level)
                    level += 1

            print("number of cycles", len(all_cycles))
            
            # print(f"Result {algorithms[i]}:", self.X)

    def count_cycles(self, Y, preference_level):
        linked = {agent : [] for agent in self.agents}

        for i, line in enumerate(self.ballot[preference_level]):
            for agent in self.agents:
                if agent in line and Y[agent] is None:
                    linked[self.agents[i]].append(agent)

        g = nx.DiGraph()
        g.add_nodes_from(linked.keys())
        
        for k, v in linked.items():
            g.add_edges_from(([(k, t) for t in v]))

        cycles = list(nx.simple_cycles(g))
        return cycles

    def update_u(self, Y, level):
        """ 
        Basic update from smart voting model proposed by Colley et al.
        """
        for agent in self.agents:
            if self.X[agent] is None:
                if self.ballot[level][agent].strip() in self.D:
                    self.X[agent] = self.ballot[level][agent]
                elif self.aggregate(Y, level, agent)[0]:
                    self.X[agent] = self.aggregate(Y, level, agent)[1]
        
        return self.X

    def update_du(self, Y, level):
        """ 
        Update function with direct vote priority from smart voting model 
        proposed by Colley et al.
        """
        for agent in self.agents:
            if self.X[agent] is None:
                if self.ballot[level][agent].strip() in self.D:
                    self.X[agent] = self.ballot[level][agent]
        
        if Y == self.X:
            for agent in self.agents:
                if self.X[agent] is None:
                    if self.aggregate(Y, level, agent)[0]:
                        self.X[agent] = self.aggregate(Y, level, agent)[1]
            
        return self.X

    def update_ru(self, Y, level):
        """ 
        Update function with random voter selection from smart voting 
        model proposed by Colley et al.
        """
        P = set()
        for agent in self.agents:
            if self.X[agent] is None:
                if self.ballot[level][agent].strip() in self.D or self.aggregate(Y, level, agent)[0]:
                    P.add(agent)
        
        if P != set():
            b = random.choice(list(P))
            if self.ballot[level][b].strip() in self.D:
                self.X[b] = self.ballot[level][b]
            else:
                self.X[b] = self.aggregate(Y, level, b)[1]
            
        return self.X

    def update_dru(self, Y, level):
        """ 
        Update function with direct vote priority and random voter selection 
        from smart voting model proposed by Colley et al.
        """
        P, Q = set(), set()
        for agent in self.agents:
            if self.X[agent] is None:
                if self.ballot[level][agent].strip() in self.D:
                    P.add(agent)
                elif self.aggregate(Y, level, agent)[0]:
                    Q.add(agent)
        
        if P != set():
            b = random.choice(list(P))
            self.X[b] = self.ballot[level][b]
        elif Q != set():
            b = random.choice(list(Q))
            self.X[b] = self.aggregate(Y, level, b)[1]
            
        return self.X

    def aggregate(self, Y, level, agent):
        """
        Computes the outcome of an agent at preference level, using a 
        direct delegated vote, majority vote or propositional logic formula.
        """
        delegation = self.ballot[level][agent].strip()
        # Compute the direct delegated vote
        if len(delegation) == 1:
            if Y[delegation] in self.D:
                return True, Y[delegation] 
        # Compute the majority vote
        elif re.findall(r"maj\((.*?)\)", delegation):
            participants = re.findall(r"\((.*?)\)", delegation)[0].split()
            
            for i, participant in enumerate(participants):
                if Y[participant] in self.D:
                    participants[i] = Y[participant]

            # Calculate outcome with most occurences
            count = Counter(participants)
            most_common = str(count.most_common(1)[0][0])

            # Check if most_common is a possible outcome and that it is the strict majority
            if most_common in self.D and count[most_common] > len(participants) /2:
                return True, most_common
        # Compute the propositional logic formula
        else:
            operations = {'0&1': '0', '1&0': '0','1&1': '1','0&0': '0', '0|1': '1', '1|0': '1','1|1': '1','0|0': '0'}

            for a in Y:
                if a in delegation and Y[a] is not None:
                    # Replace all agents in string with its corresponding outcome
                    delegation = delegation.replace(a, Y[a])

            # Delete all spaces from string
            delegation = delegation.replace(" ", "")

            # Solve all negations in string
            for negation in re.findall('~.', delegation):
                delegation = delegation.replace(negation, negation[1])
            
            # Keep going until there is an outcome
            while len(delegation) != 1:
                # Compute outcome of complete logic formula
                if delegation[0:3] in operations:
                    delegation = operations[delegation[0:3]] + delegation[3:]

                elif '0' in delegation[0:3]:
                    # A logic formula with '0' and '&' always results in '0'
                    if re.search(r"0&.", delegation[0:3]) or re.search(r".&0", delegation[0:3]):
                        delegation = '0' + delegation[3:]
                    # The outcome cannot yet be determined
                    elif re.search(r"0|.", delegation[0:3]) or re.search(r".|0", delegation[0:3]):
                        delegation = '?' + delegation[3:]

                elif '1' in delegation[0:3]:
                    # A logic formula with '1' and '|' always results in '1'
                    if re.search(r"1|.", delegation[0:3]) or re.search(r".|1", delegation[0:3]):
                        delegation = '1' + delegation[3:]
                    # The outcome cannot yet be determined
                    elif re.search(r"1&.", delegation[0:3]) or re.search(r".&1", delegation[0:3]):
                        delegation = '?' + delegation[3:]

                else:
                    return False, ""

            return True, str(delegation)

        return False, ""
       

def create_ballot(folder, num_agents, preference_level):
    """
    Creates dataframe of smart ballot with the given parameters.
    """
    agents = list(string.ascii_uppercase)[:num_agents]
    dataframe = pd.read_csv(folder, names = [i for i in range(1,preference_level+1)], dtype = str)
    dataframe.index = agents[:num_agents]
    dataframe = dataframe.fillna('-')

    return dataframe, agents


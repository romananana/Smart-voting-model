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

    def unravel(self):
        algorithms = ['U', 'DU', 'RU', 'DRU']
        result = {}

        # Calculate result for all of the unravelling procedures
        for i, func in enumerate([self.update_u, self.update_du, self.update_ru, self.update_dru]):
            reset_outcome(self)
            while None in self.X.values():
                level = 1
                Y = copy.deepcopy(self.X)
                while Y == self.X:
                    self.X = func(Y, level)
                    level += 1

            result[algorithms[i]] = self.X

        return result

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
        delegation = self.ballot[level][agent]

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

            delegation = delegation.replace(' ', '')

            # Solve all negations in string
            for negation in re.findall('~.', delegation):
                delegation = delegation.replace(negation, negation[1])

            # Keep going until there is an single correct outcome
            while len(delegation) != 1:
                brackets_delegation = copy.deepcopy(delegation)

                # Check if there are brackets in the formula
                if re.search(r"\(.*\)", delegation):
                    # Find most inner brackets
                    while re.search(r"\(.*\)", brackets_delegation):
                        brackets_delegation = re.findall(r"\(.*\)", brackets_delegation)[0][1:-1]

                    updated_delegation = replace_formula(brackets_delegation, operations)

                    if updated_delegation:
                        delegation = delegation.replace('(' + brackets_delegation + ')', updated_delegation)
                    else:
                        # Propositional logic in brackets is not solvable in this preference level
                        return False, ""

                else:
                    delegation = replace_formula(delegation, operations)

                    # Propositional logic is not solvable in this preference level
                    if not delegation:
                        return False, ""

            # delegation has a correct outcome
            if delegation != '?':
                return True, str(delegation)

        return False, ""

def reset_outcome(Voting):
    Voting.X = {}
    for agent in Voting.agents:
        Voting.X[agent] = None

def create_ballot(folder, num_agents, preference_level):
    """
    Creates dataframe of smart ballot with the given parameters.
    """
    agents = list(string.ascii_uppercase)[:num_agents]
    dataframe = pd.read_csv(folder, names = [i for i in range(1,preference_level+1)], dtype = str)
    dataframe.index = agents[:num_agents]
    dataframe = dataframe.fillna('-')

    return dataframe, agents

def replace_formula(delegation, operations):
    # Compute outcome of complete logic formula
    while len(delegation) != 1:
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
            return False

    return delegation

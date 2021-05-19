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
from cycles import find_cycles, cycle_duplicates

class SmartVoting:
    def __init__(self, df, agents):
        self.profile = df       # Delegation profile
        self.D = ['0', '1']     # Possible outcome
        self.agents = agents

    def unravel(self):
        algorithms = ['U', 'DU', 'RU', 'DRU']
        result = {}
        number_of_cycles = {}

        # Calculate result for all of the unravelling procedures
        for i, func in enumerate([self.update_u, self.update_du, self.update_ru, self.update_dru]):
            reset_outcome(self)
            cycles = set()

            while None in self.X.values():
                level = 1
                Y = copy.deepcopy(self.X)
                while Y == self.X:
                    for cycle in find_cycles(self,  Y, level):
                        if not cycle_duplicates(cycles, cycle):
                            cycles.add(tuple(cycle))

                    self.X = func(Y, level)
                    level += 1

            number_of_cycles[algorithms[i]] = len(cycles)
            result[algorithms[i]] = self.X

        return result, number_of_cycles

    def update_u(self, Y, level):
        """ 
        Basic update from smart voting model proposed by Colley et al.
        """
        for agent in self.agents:
            if self.X[agent] is None:
                if self.profile[level][agent].strip() in self.D:
                    self.X[agent] = self.profile[level][agent]
                elif True:
                    boolean, outcome = self.aggregate(Y, level, agent)
                    if boolean:
                        self.X[agent] = outcome
        
        return self.X

    def update_du(self, Y, level):
        """ 
        Update function with direct vote priority from smart voting model 
        proposed by Colley et al.
        """
        for agent in self.agents:
            if self.X[agent] is None:
                if self.profile[level][agent].strip() in self.D:
                    self.X[agent] = self.profile[level][agent]
        
        if Y == self.X:
            for agent in self.agents:
                if self.X[agent] is None:
                    boolean, outcome = self.aggregate(Y, level, agent)
                    if boolean:
                        self.X[agent] = outcome
            
        return self.X

    def update_ru(self, Y, level):
        """ 
        Update function with random voter selection from smart voting 
        model proposed by Colley et al.
        """
        P = set()
        for agent in self.agents:
            if self.X[agent] is None:
                if self.profile[level][agent].strip() in self.D or self.aggregate(Y, level, agent)[0]:
                    P.add(agent)
        
        if P != set():
            b = random.choice(list(P))
            if self.profile[level][b].strip() in self.D:
                self.X[b] = self.profile[level][b]
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
                if self.profile[level][agent].strip() in self.D:
                    P.add(agent)
                elif self.aggregate(Y, level, agent)[0]:
                    Q.add(agent)
        
        if P != set():
            b = random.choice(list(P))
            self.X[b] = self.profile[level][b]
        elif Q != set():
            b = random.choice(list(Q))
            self.X[b] = self.aggregate(Y, level, b)[1]
            
        return self.X

    def aggregate(self, Y, level, agent):
        """
        Computes the outcome of an agent at preference level, using a 
        direct delegated vote, majority vote or propositional logic formula.
        """
        delegation = self.profile[level][agent]

        # Compute the direct delegated vote
        if len(delegation) == 1:
            if Y[delegation] in self.D:
                return True, Y[delegation] 

        # Compute the voting rule
        elif re.findall(r"rule\((.*?)\)", delegation):
            boolean, outcome = compute_votingrule(self, Y, delegation)
            if boolean:
                return True, outcome
                
        # Compute the propositional logic formula
        else:
            boolean, outcome = compute_formula(Y, delegation)
            if boolean:
                return True, outcome

        return False, ""


def reset_outcome(Voting):
    Voting.X = {}
    for agent in Voting.agents:
        Voting.X[agent] = None

def create_profile(folder, num_agents, preference_level):
    """
    Creates dataframe of smart profile with the given parameters.
    """
    agents = list(string.ascii_uppercase)[:num_agents]
    dataframe = pd.read_csv(folder, sep= ', ', names = [i for i in range(1,preference_level+1)], dtype = str, engine='python')
    dataframe.index = agents[:num_agents]
    dataframe = dataframe.fillna('-')

    return dataframe, agents

def compute_votingrule(Voting, Y, delegation):
    participants, percentage = re.findall(r"\((.*?)\)", delegation)[0].split(',')
    participants = participants.split()
    percentage = int(percentage[:-1])/100

    for i, participant in enumerate(participants):
        if Y[participant] in Voting.D:
            participants[i] = Y[participant]

    # Calculate outcome with most occurences
    count = Counter(participants)
    most_common = str(count.most_common(1)[0][0])

    # Check if most_common is a possible outcome and that it is the strict majority
    if most_common in Voting.D and count[most_common]/len(participants) >= percentage:
        return True, most_common

    return False, ''

def compute_formula(Y, delegation):
    operations = {'0&1': '0', '1&0': '0','1&1': '1','0&0': '0', '0|1': '1', '1|0': '1','1|1': '1','0|0': '0'}

    # Replace all agents in string with its corresponding outcome
    for a in Y:
        if a in delegation and Y[a] is not None:
            delegation = delegation.replace(a, Y[a])

    delegation = delegation.replace(' ', '')

    # Solve all negations in string
    for negation in re.findall('~.', delegation):
        if negation == '~1':
            delegation = delegation.replace(negation, '0')
        elif negation == '~0':
            delegation = delegation.replace(negation, '1')
        else:
            delegation = delegation.replace(negation, negation[1])
                        
    # Keep going until there is an single correct outcome
    while len(delegation) != 1:
        brackets_delegation = copy.deepcopy(delegation)

        # Check if there are brackets in the formula
        if re.search(r"\(.*\)", delegation):
            # Find most inner brackets
            while re.search(r"\(.*\)", brackets_delegation):
                brackets_delegation = re.findall(r"\(.*\)", brackets_delegation)[0][1:-1]

            boolean, updated_delegation = replace_formula(brackets_delegation, operations)
            delegation = delegation.replace('(' + brackets_delegation + ')', updated_delegation)

        else:
            boolean, delegation = replace_formula(delegation, operations)

        # Propositional logic is not solvable in this preference level
        if not boolean:
            return False, ""

    # delegation has a correct outcome
    if delegation != '?':
        return True, str(delegation)
    else:
        return False, ''

def replace_formula(delegation, operations):
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
            return False, ''

    return True, delegation
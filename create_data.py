"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:       This file contains a function that generates a random smart ballot 
            given the parameters for the smart voting model proposed by Colley et al. 
"""

import random
import numpy as np
import string
import copy
from sympy.logic.boolalg import to_dnf, is_dnf
import re
from itertools import combinations
import math

def create_data(file, num_agents, preference_level, delegation_bounds=[0,1], percentage='51%'):
    agents = list(string.ascii_uppercase)[:num_agents]
    outcome = ['0', '1']
    operators = [['&', '|'], 'rule']
    lower_bound, upper_bound = delegation_bounds[0], delegation_bounds[1]

    with open(file, 'w') as new_file:
        for i in range(num_agents):
            # Create list with all possible agents to which an agent can delegate
            possible_agents = copy.deepcopy(agents)
            possible_agents.pop(i)

            # Get the probability that an agent will delegate his vote
            prob_delegation = np.random.uniform(low=lower_bound, high=upper_bound, size=None)
            # Create empty delegation ballot
            ballot = ''

            for j in range(preference_level):
                # Agent chooses to delegate  his vote or directly vote with a wieghted uniform distribution
                choice = random.choices(['delegate', 'direct vote'], weights = [prob_delegation, 1-prob_delegation])
                
                # In the last preference level, the agent is obligated to vote directly
                if choice[0] == 'direct vote' or (j+1) == preference_level or (j+1) == (num_agents - 1):
                    ballot += random.choice(outcome) + ', '
                    # The delegation ballot of an agent is complete when he directly votes
                    break
                elif choice[0] == 'delegate':
                    counter = 0
                    # Agents can try 15 times to make a new delegation
                    while counter < 15:
                        delegation = ''
                        # Agent chooses random subset of agent to whom he wants to delegate
                        candidates = random.sample(possible_agents, random.choice(range(1, len(possible_agents)+1)))

                        # Agent wants to delegate to a single agent
                        if len(candidates) == 1:
                            delegation += candidates[0] + ', '
                        else:
                            # Agent chooses to use a majority vote or to use propositional logic
                            operator = random.choice(operators)
                            if operator == 'rule':
                                delegation = create_votingrule(delegation, candidates, percentage)
                            else: 
                                delegation = create_formula(delegation, candidates, only_conjunctions=False)

                        # Check if the delegation did not already occur in the ballot
                        if delegation not in ballot.split(', '):
                            if re.search(r"51%", delegation) and ballot != '':
                                if not duplicate_majority(delegation, ballot):
                                    pass

                            ballot += delegation
                            break

                        counter += 1

                    if counter == 15:
                        ballot += random.choice(outcome) + ', '
        
            # Write delegation ballot to file
            new_file.write(ballot[:-2] + "\n")

def create_votingrule(delegation, candidates, percentage):
    delegation += 'rule('
    candidates = sorted(candidates)
    for c in candidates:
        delegation += c + ' '

    return delegation[:-1] + f',{percentage}), '

def create_formula(delegation, candidates, only_conjunctions = False):
    outside_brackets = []
    inside_brackets = []

    while len(delegation) <= 20:
        no_spaces = copy.deepcopy(delegation.replace(' ', ''))
        max_agents = int(math.ceil((20 - len(no_spaces))/2))

        # Choose candidates for in bracket
        if max_agents < len(candidates):
            formula_candidates = sorted(random.sample(candidates, random.choice(range(1, max_agents + 1 ))))
        else:
            formula_candidates = sorted(random.sample(candidates, random.choice(range(1, len(candidates)+1 ))))

        if len(formula_candidates) != 1:
            temp_agents = []
            temp_delegation = ''

            for c in formula_candidates:
                temp_agents.append(random.choice(['', '~']) + c)
                temp_delegation += temp_agents[-1] + ' & '

            if temp_agents not in inside_brackets:
                delegation += '('
                delegation += temp_delegation[:-3]
                delegation += ')' + ' | '
        else:
            if only_conjunctions == False:
                if formula_candidates[0] not in outside_brackets:
                    delegation += random.choice(['', '~']) + formula_candidates[0] + ' | '
                    outside_brackets.append(formula_candidates[0])

        if random.choice([True, False]) and delegation != '':
            break
    
    delegation = to_dnf(delegation[:-3].lower())
    delegation = str(delegation).upper() + ', '

    return delegation

def duplicate_majority(delegation, ballot):
    agents, _ = re.findall(r"\((.*?)\)", delegation)[0].split(',')
    agents = agents.split()
    
    comb = list(combinations(agents, len(agents)-1))
    
    for i, c in enumerate(comb):
        comb[i] = '&'.join(c)
    
    for delegate in ballot.split(', '):
        brackets = re.findall(r"\((.*?)\)", delegate)
        
        if set(comb) == set(brackets):
            for b in brackets:
                delegate = delegate.replace('('+b+')', '')
            
            if not re.search(r"[a-zA-Z]", delegate):
                return True
                
    return False


if __name__ == "__main__":
    # State parameters of smart ballot
    preference_level = 4
    num_agents = 5
    delegation_bound_lower = 0
    delegation_bound_upper = 1
    amount_ballots = 10

    for i in range(1, amount_ballots + 1):
        file = f"{i}_{num_agents}_{preference_level}_{delegation_bound_lower}_{delegation_bound_upper}.csv"
        
        # Change path to where you want your data to be
        create_data(f"data/{file}", num_agents, preference_level, [delegation_bound_lower, delegation_bound_upper])
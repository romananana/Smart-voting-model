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
from sympy.logic.boolalg import to_dnf
import re
from itertools import combinations
import math

def create_data(file, number_of_agents, maximal_delegations, delegation_bounds, profile):
    """
    Creates a valid smart profile according to the parameters.
    """
    agents = list(string.ascii_uppercase)[:number_of_agents]
    outcome = ['0', '1']

    lower_bound, upper_bound = delegation_bounds[0], delegation_bounds[1]

    with open(file, 'w') as new_file:
        for i in range(number_of_agents):
            # Create list with all possible agents to which an agent can delegate
            possible_agents = copy.deepcopy(agents)
            possible_agents.pop(i)

            # Get the probability that an agent will delegate his vote
            prob_delegation = np.random.uniform(lower_bound, upper_bound, size=None)
            # Create empty delegation ballot
            ballot = ''

            for j in range(maximal_delegations):
                # Agent chooses to delegate  his vote or directly vote with a wieghted uniform distribution
                choice = random.choices(['delegate', 'direct vote'], weights = [prob_delegation, 1-prob_delegation])
                
                # In the last preference level, the agent is obligated to vote directly
                if choice[0] == 'direct vote' or (j+1) == maximal_delegations:
                    ballot += random.choice(outcome) + ', '
                    # The delegation ballot of an agent is terminated when one votes directly votes
                    break
                elif choice[0] == 'delegate':
                    counter = 0
                    # Agents can try 10 times to make a new delegation
                    while counter < 10:
                        delegation = ''
                        # Agent chooses random subset of agent to whom he wants to delegate
                        candidates = random.sample(possible_agents, random.choice(range(1, len(possible_agents)+1)))

                        # Agent wants to delegate to a single agent
                        if len(candidates) == 1:
                            if profile == 'no negation':
                                delegation += candidates[0] + ', '
                            else:
                                delegation += random.choice(['', '~']) + candidates[0] + ', '

                        else:
                            delegation_type = ""
                            if profile == 'combined':
                                delegation_type = random.choice(['quota', 'logic'])

                            if profile == 'quota' or delegation_type == 'quota':
                                delegation = create_quotarule(delegation, candidates, profile)
                            elif profile == 'logic' or profile == 'no negation' or delegation_type == 'logic': 
                                delegation = create_formula(delegation, candidates, profile)

                        # Check if the delegation did not already occur in the ballot
                        if delegation not in ballot.split(', '):
                            if profile == 'combined':
                                # Check whether the quota rule already exists in the ballot as logical formula
                                if re.search(r"quota\((.*?)\)", delegation):
                                    quota_agents, quota = re.findall(r"quota\((.*?)\)", delegation)[0].split(',')
                                    quota_agents = quota_agents.split()

                                    if len(quota_agents) == int(quota):
                                        if duplicate_unanimity(delegation, ballot):
                                            counter += 1
                                            continue
                                    else:
                                        if duplicate_majority(delegation, ballot):
                                            counter += 1
                                            continue 
                            
                            ballot += delegation
                            break

                        counter += 1

                    if counter == 10:
                        ballot += random.choice(outcome) + ', '
                        break
        
            # Write delegation ballot to file
            new_file.write(ballot[:-2] + "\n")

def create_quotarule(delegation, candidates, profile):
    """
    Create quota rule
    """
    delegation += 'quota('
    candidates = sorted(candidates)

    if profile == 'combined':
        quota = math.ceil(len(candidates) * 0.51)
        quota = random.choice([quota, len(candidates)])
    else:
        quota = random.choice(range(1, len(candidates)+1))
    
    for c in candidates:
        delegation += c + ' '

    return delegation[:-1] + f',{quota}), '

def create_formula(delegation, candidates, profile):
    """
    Create formula of propostional logic
    """
    single_character = []
    outside = []

    while len(delegation) <= 20:
        no_spaces = copy.deepcopy(delegation.replace(' ', ''))
        max_agents = int(math.ceil((20 - len(no_spaces))/2))

        # Choose candidates for in bracket
        if max_agents < len(candidates):
            formula_candidates = sorted(random.sample(candidates, random.choice(range(1, max_agents + 1 ))))
        else:
            formula_candidates = sorted(random.sample(candidates, random.choice(range(1, len(candidates)+1 ))))

        if profile == 'no negation':
            negations = ['']
        else:
            negations = ['', '~']

        subformula = ""
        temp_agents = []

        if len(formula_candidates) != 1:
            subformula += '('
            for c in sorted(formula_candidates):
                if f'~{c}' in single_character:
                    c = f'~{c}'
                    subformula +=  c + ' & '
                elif c in single_character:
                    subformula +=  c + ' & '
                else:
                    c = random.choice(negations) + c
                    subformula +=  c + ' & '

                    temp_agents.append(c)

            subformula = subformula[:-3] + ')'
            if subformula not in delegation:
                delegation += subformula + ' | '
                for c in temp_agents:
                    single_character.append(c)
        else:
            c = formula_candidates[0]

            if f'~{c}' in single_character:
                subformula += f"~{c}"
            elif c in single_character:
                subformula += c 
            else:
                c = random.choice(negations) + c 
                subformula += c 

            if subformula not in outside:
                delegation += subformula + ' | '
                single_character.append(subformula)
                outside.append(subformula)

        if random.choice([True, False]) and delegation != '':
            break

    delegation = to_dnf(delegation[:-3].lower())
    delegation = str(delegation).upper() + ', '

    return delegation

def duplicate_majority(delegation, ballot):
    """
    Check if quota rule which represents the majority occurs in the ballot
    as a formula of propositional logic.
    return: True if it is a duplicate
            False if it is not a duplicate
    """
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

def duplicate_unanimity(delegation, ballot):
    """
    Check if quota rule which represents the unanimity occurs in the ballot
    as a formula of propositional logic.
    return: True if it is a duplicate
            False if it is not a duplicate
    """
    agents, _ = re.findall(r"\((.*?)\)", delegation)[0].split(',')
    agents = agents.split()
    delegate = ' & '.join(agents) 

    if delegate in ballot.split(', '):
        return True

    return False
    
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

def create_data(file, num_agents, preference_level, delegation_bounds=[0,1]):
    agents = list(string.ascii_uppercase)[:num_agents]
    outcome = ['0', '1']
    operators = [['&', '|'], 'maj']
    lower_bound = delegation_bounds[0]
    upper_bound = delegation_bounds[1]

    with open(f"data/{file}", 'w') as new_file:
        for i in range(num_agents):
            # Create list with all possible agents to which an agent can delegate
            possible_agents = copy.deepcopy(agents)
            possible_agents.pop(i)

            # Get the probability that an agent will delegate his vote
            prob_delegation = np.random.uniform(low=lower_bound, high=upper_bound, size=None)
            # Create empty delegation profile
            delegation_profile = ''

            for i in range(preference_level):
                # Agent chooses to delegate  his vote or directly vote with a wieghted uniform distribution
                choice = random.choices(['delegate', 'direct vote'], weights = [prob_delegation, 1-prob_delegation])
                
                # In the last preference level, the agent is obligated to vote directly
                if choice[0] == 'direct vote' or i == (preference_level - 1):
                    delegation_profile += random.choice(outcome) + ','
                    # The delegation profile of an agent is complete when he directly votes
                    break
                elif choice[0] == 'delegate':
                    # Agent chooses random subset of agent to whom he wants to delegate
                    candidates = random.sample(possible_agents, random.choice(range(1, len(possible_agents)+1)))

                    # Agent wants to delegate to a single agent
                    if len(candidates) == 1:
                        delegation_profile += candidates[0] + ','
                        continue

                    # Agent chooses to use a majority vote or to use propositional logic
                    operator = random.choice(operators)
                    if operator == 'maj':
                        # Add delegation for delegation profile
                        delegation_profile += operator + '('
                        for c in candidates:
                            delegation_profile += c + ' '

                        delegation_profile = delegation_profile[:-1] + '),'
                    else: 
                        # Choose random a single or multiple operator(s)
                        operator = random.sample(operator, random.choice(range(1, len(operator)+1)))

                        # Add delegation for delegation profile
                        for c in candidates:
                            
                            delegation_profile += random.choice(['', '~']) + c + random.choice(operator)

                        delegation_profile = delegation_profile[:-1] + ','
                    
            # Write delegation profile to file
            new_file.write(delegation_profile[:-1] + "\n")
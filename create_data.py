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

    with open(file, 'w') as new_file:
        for i in range(num_agents):
            # Create list with all possible agents to which an agent can delegate
            possible_agents = copy.deepcopy(agents)
            possible_agents.pop(i)
            # Create list with all delegations for an agent
            delegations_agent = []

            # Get the probability that an agent will delegate his vote
            prob_delegation = np.random.uniform(low=lower_bound, high=upper_bound, size=None)
            # Create empty delegation profile
            delegation_profile = ''

            for j in range(preference_level):
                # Agent chooses to delegate  his vote or directly vote with a wieghted uniform distribution
                choice = random.choices(['delegate', 'direct vote'], weights = [prob_delegation, 1-prob_delegation])
                
                # In the last preference level, the agent is obligated to vote directly
                if choice[0] == 'direct vote' or j == (preference_level - 1):
                    delegation_profile += random.choice(outcome) + ','
                    # The delegation profile of an agent is complete when he directly votes
                    break
                elif choice[0] == 'delegate':
                    while True:
                        delegation = ''
                        # Agent chooses random subset of agent to whom he wants to delegate
                        candidates = random.sample(possible_agents, random.choice(range(1, len(possible_agents)+1)))

                        # Agent wants to delegate to a single agent
                        if len(candidates) == 1:
                            delegation += candidates[0] + ','
                        else:
                            # Agent chooses to use a majority vote or to use propositional logic
                            operator = random.choice(operators)
                            if operator == 'maj':
                                # Add delegation for delegation profile
                                delegation += operator + '('
                                for c in candidates:
                                    delegation += c + ' '

                                delegation = delegation[:-1] + '),'
                            else: 
                                length = len(candidates)
                                while candidates != []:
                                    brackets_candidates = random.sample(candidates, random.choice(range(1, len(candidates)+1)))
                                    # Choose random a single or multiple operator(s)
                                    operator = random.sample(operator, random.choice(range(1, len(operator)+1)))
                                    
                                    if len(brackets_candidates) != 1 and len(brackets_candidates) != length:
                                        delegation += '('

                                    # Add delegation to string
                                    for c in brackets_candidates:
                                        delegation += random.choice(['', '~']) + c + random.choice(operator)
                                        candidates.remove(c)

                                    if len(brackets_candidates) != 1 and len(brackets_candidates) != length:
                                        delegation = delegation[:-1]
                                        delegation += ')' + random.choice(operator)

                                delegation = delegation[:-1] + ','

                        # Check if the delegation did not already occur
                        if delegation not in delegations_agent:
                            delegation_profile += delegation
                            delegations_agent.append(delegation)
                            break
                    
            # Write delegation profile to file
            new_file.write(delegation_profile[:-1] + "\n")


if __name__ == "__main__":
    # State parameters of smart ballot
    preference_level = 4
    num_agents = 5
    delegation_bound_lower = 0.8
    delegation_bound_upper = 1
    amount_ballots = 10

    for i in range(1, amount_ballots + 1):
        file = f"{i}_{num_agents}_{preference_level}_{delegation_bound_lower}_{delegation_bound_upper}.csv"
        
        # Change path to where you want your data to be
        create_data(f"data/{file}", num_agents, preference_level, [delegation_bound_lower, delegation_bound_upper])
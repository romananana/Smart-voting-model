"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:        
"""

from setup import SmartVoting, create_ballot
from data import create_data

if __name__ == "__main__":
    # State parameters of smart ballot
    preference_level = 3
    num_agents = 5
    delegation_bound_lower = 0
    delegation_bound_upper = 1
    amount_ballots = 10

    for i in range(1, amount_ballots + 1):
        file = f"{i}_{num_agents}_{preference_level}_{delegation_bound_lower}_{delegation_bound_upper}.csv"
        create_data(file, num_agents, preference_level, [delegation_bound_lower, delegation_bound_upper])

        # Create dataframe 
        ballot, agents = create_ballot(f"data/{file}", num_agents, preference_level)
        print(ballot)

        Voting = SmartVoting(ballot, agents)
        Voting.calculate_output()
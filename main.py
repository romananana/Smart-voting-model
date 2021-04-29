"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:        
"""

from setup import SmartVoting, create_ballot
from create_data import create_data

if __name__ == "__main__":
    # State parameters of smart ballot
    preference_level = 4
    num_agents = 5
    delegation_bound_lower = 0
    delegation_bound_upper = 1
    amount_ballots = 10

    for i in range(1, amount_ballots + 1):
        file = f"{i}_{num_agents}_{preference_level}_{delegation_bound_lower}_{delegation_bound_upper}.csv"

        # Create dataframe of datafile
        # Change path to where your data is
        ballot, agents = create_ballot(f"data/{file}", num_agents, preference_level)

        # Create smart voting model
        Voting = SmartVoting(ballot, agents)
        # Unravel the ballot
        outcome = Voting.unravel()

        print(outcome, "\n")
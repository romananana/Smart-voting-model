"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:        
"""

from setup import SmartVoting, create_profile
from create_data import create_data

if __name__ == "__main__":
    # State parameters of smart profile
    preference_level = 4
    num_agents = 5
    delegation_bound_lower = 0
    delegation_bound_upper = 1
    amount_profiles = 10

    for i in range(1, amount_profiles + 1):
        file = f"{i}_{num_agents}_{preference_level}_{delegation_bound_lower}_{delegation_bound_upper}.csv"
        create_data(f"data/{file}", num_agents, preference_level)

        # Create dataframe of datafile
        # Change path to where your data is
        profile, agents = create_profile(f"data/{file}", num_agents, preference_level)

        print(profile)
        # Create smart voting model
        Voting = SmartVoting(profile, agents)
        # Unravel the profile
        outcome, number_of_cycles = Voting.unravel()

        print("Cycles per unravelling procedure", number_of_cycles, "\n")
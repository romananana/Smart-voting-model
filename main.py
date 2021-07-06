"""
DISCLAIMER: This file was created for the thesis of Romana Wilschut for the 
            bachelor ‘Artificial Intelligence’ at the University of Amsterdam.
NAME:       Romana Wilschut 
UVA ID:     12156884
INFO:       This files creates valid smart profiles according to the parameters.
            These are unravelled for each unravelling procedure, and the number
            of cycles that arise are printed.
"""

from setup import SmartVoting, create_profile
from create_data import create_data

if __name__ == "__main__":
    ########## CHANGE PARAMETERS ##########
    maximal_delegations = 4 
    number_of_agents = 5
    delegation_bound_lower = 0 # value between 0 and 1
    delegation_bound_upper = 1 # value between 0 and 1
    type_of_profile = 'no negation' # can be 'combined', 'quota', 'logic' or 'no negation'
    amount_profiles = 10
    #######################################

    for i in range(1, amount_profiles + 1):
        file = f"{i}_{number_of_agents}_{maximal_delegations}_{delegation_bound_lower}_{delegation_bound_upper}.csv"

        ########## CHANGE PATH TO DESIRED FOLDER ##########
        create_data(f"data/{file}", number_of_agents, maximal_delegations, [delegation_bound_lower, delegation_bound_upper], type_of_profile)
        profile, agents = create_profile(f"data/{file}", number_of_agents, maximal_delegations)
        ###################################################
        print("Valid smart profile\n", profile)

        # Create smart voting model
        Voting = SmartVoting(profile, agents)
        # Unravel the profile
        outcome, number_of_cycles = Voting.unravel()

        print("\nFinal collective decision\n", outcome, "\n")
        print("Cycles per unravelling procedure\n", number_of_cycles, "\n")
        
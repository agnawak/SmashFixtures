import random, math
import numpy as np

def luckydraw(category):
    if len(category.members) == 0:
        return None
    return random.choice(category.members)

def choose_and_remove(category, team):
    chosen_player = luckydraw(category)

    if chosen_player is None:
        return category, team  # nothing to remove

    team.members = np.append(team.members, chosen_player)
    team.total_points += category.points
    category.members = category.members[category.members != chosen_player]

    return category, team


def create_fixture(players):
    team = Team([],0)
    
    for _ in range(6):  # team size
        available = [p for p in players if len(p.members) > 0]

        if not available:
            break  # no players left anywhere

        # Prefer larger arrays automatically
        category = max(available, key=lambda x: len(x.members))

        category, team = choose_and_remove(category, team)
    
    return team

class Tier:
    def __init__(self, data, points):
        # Store a NumPy array as an attribute
        self.members = np.array(data, dtype=str)
        self.points = points

class Team:
    def __init__(self, members, total_points):
        self.members = np.array(members, dtype=str)
        self.total_points = total_points

def main():
    rounds = 10
    teams = []

    for j in range(math.ceil(rounds/4)):
        menA = ['man1', 'man2', 'man3', 'man4']
        menB = ['man7', 'man8', 'man9', 'man10', 'man11', 'man12', 'man13']
        menC = ['man14', 'man15', 'man16', 'man17', 'man18']
        womenA = ['woman1'] #, 'woman2', 'woman3', 'woman4'
        womenB = ['woman7', 'woman8']#, 'woman9', 'woman10'
        setter = ['setter1', 'setter2', 'setter3', 'setter4', 'setter5']

        TierAMen = Tier(menA, 3)
        TierBMen = Tier(menB, 2)
        TierCMen = Tier(menC, 1)
        TierSetter = Tier(setter, 3)
        TierAWomen = Tier(womenA, 2)
        TierBWomen = Tier(womenB, 1)

        players = [TierAMen, TierBMen, TierCMen, TierSetter, TierAWomen, TierBWomen]
        total_teams = int((len(menA)+len(menB)+len(menC)+len(womenA)+len(womenB)+len(setter))/6)
        for i in range(total_teams):
            team = create_fixture(players)
            teams.append(team)

    for index, team in enumerate(teams):
        print(f"Team {index+1} : (points value at: {team.total_points})")
        print(team.members)
        print("\n")

main()
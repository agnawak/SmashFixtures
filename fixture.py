import random, math

def luckydraw(category):
    return category[random.randint(0, len(category)-1)]

def remove_called_players(category, team):
    for j, player in enumerate(category):
        if player in team:
            category.remove(player)
            return category
    return category

def choose_and_remove(category, team):
    team.append(luckydraw(category))
    new_category = remove_called_players(category, team)
    return new_category, team

def create_fixture(women, setter, men, existing_team, count):
    team = []
    next_women = remove_called_players(women, existing_team)
    next_setter = remove_called_players(setter, existing_team)
    next_men = remove_called_players(men, existing_team)

    next_new_women, team = choose_and_remove(next_women, team)
    next_new_setter, team = choose_and_remove(next_setter, team)
    next_new_men, team = choose_and_remove(next_men, team)

    combined_category = next_new_setter + next_new_men
    
    for i in range(3):
        team.append(luckydraw(combined_category))
        combined_category = remove_called_players(combined_category, team)
    
    return team

def main():
    rounds = 10
    teams = []

    # new_women, new_setter, new_men, team = create_fixture(women, setter, men, team)
    # teams.append(team)
    for j in range(math.ceil(rounds/4)):
    # for j in range(rounds/3):
        men = ['alif', 'ba', 'ta', 'tha', 'jeem', 'ha', 'kha', 'dal', 'thal', 'ra', 'zay']
        women = ['meem', 'noon', 'hana', 'waw', 'ya']
        setter = ['ali', 'abu', 'ahok', 'mimi', 'noona', 'hani', 'wawa', 'zain']
        team = []
        for i in range(4):
            team = create_fixture(women, setter, men, team, i+1)
            teams.append(team)

    for index, team in enumerate(teams):
        print(f"Team {index+1} : ")
        print(team)
        print("\n")

main()
import random, math
import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

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
        menA = ['Arif', 'Nysh', 'Jad']
        menB = ['Idlan', 'Fahmi', 'adly', 'Irwan', 'Dan', 'Lan', 'Jabba', 'Haikal']
        menC = ['Rhulz', 'yeng', 'Paan', 'amsyar', 'Izz', 'Odeng']
        womenA = ['Yana', 'Hana'] #, 'woman2', 'woman3', 'woman4'
        womenB = ['Taca']#, 'woman9', 'woman10'
        setter = ['mirul', 'ikmal', 'Alif', 'mkA']

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

    # Export teams to Excel on a single sheet with two teams per row
    excel_file = '04_01_2026_Fixtures.xlsx'
    wb = Workbook()
    ws = wb.active
    ws.title = "All Teams"
    
    current_row = 1
    
    for idx in range(0, len(teams), 2):
        # Left team (odd team number)
        team1 = teams[idx]
        ws[f'A{current_row}'] = f"Team {idx+1}"
        ws[f'A{current_row}'].font = Font(bold=True, size=12)
        row_offset = 1
        
        for player in team1.members:
            ws[f'A{current_row + row_offset}'] = player
            ws[f'A{current_row + row_offset}'].alignment = Alignment(horizontal='center', vertical='center')
            row_offset += 1
        
        max_height = row_offset
        
        # Right team (even team number) - if it exists
        if idx + 1 < len(teams):
            team2 = teams[idx + 1]
            ws[f'B{current_row}'] = f"Team {idx+2}"
            ws[f'B{current_row}'].font = Font(bold=True, size=12)
            row_offset = 1
            
            for player in team2.members:
                ws[f'B{current_row + row_offset}'] = player
                ws[f'B{current_row + row_offset}'].alignment = Alignment(horizontal='center', vertical='center')
                row_offset += 1
            
            max_height = max(max_height, row_offset)
        
        # Move to next row pair
        current_row += max_height + 1
    
    wb.save(excel_file)
    print(f"\nTeams exported to {excel_file}")

main()
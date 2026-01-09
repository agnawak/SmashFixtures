import random, math
import numpy as np
import pandas as pd
from openpyxl import Workbook, load_workbook
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

def read_tier_list(excel_file):
    """
    Read tier list from Excel file with format:
    Column A: men names
    Column B: men tier (A/B/C)
    Column D: women names
    Column E: women tier (A/B/C)
    Column G: setter names
    """
    wb = load_workbook(excel_file)
    ws = wb.active
    
    menA, menB, menC = [], [], []
    womenA, womenB, womenC = [], [], []
    setter = []
    
    # Read men (columns A and B)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=1).value  # Column A
        tier = ws.cell(row=row, column=2).value  # Column B
        if name:
            if tier == 'A':
                menA.append(name)
            elif tier == 'B':
                menB.append(name)
            elif tier == 'C':
                menC.append(name)
    
    # Read women (columns D and E)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=4).value  # Column D
        tier = ws.cell(row=row, column=5).value  # Column E
        if name:
            if tier == 'A':
                womenA.append(name)
            elif tier == 'B':
                womenB.append(name)
            elif tier == 'C':
                womenC.append(name)
    
    # Read setter (column G)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=7).value  # Column G
        if name:
            setter.append(name)
    
    wb.close()
    
    return {
        'menA': menA,
        'menB': menB,
        'menC': menC,
        'womenA': womenA,
        'womenB': womenB,
        'womenC': womenC,
        'setter': setter
    }

def main():
    # Read tier list from Excel file
    tier_list_file = 'tier_list.xlsx'  # Change this to your tier list file name
    tier_data = read_tier_list(tier_list_file)
    
    rounds = 12
    teams = []

    for j in range(math.ceil(rounds/4)):
        menA = tier_data['menA'].copy()
        menB = tier_data['menB'].copy()
        menC = tier_data['menC'].copy()
        womenA = tier_data['womenA'].copy()
        womenB = tier_data['womenB'].copy()
        womenC = tier_data['womenC'].copy()
        setter = tier_data['setter'].copy()

        TierAMen = Tier(menA, 3)
        TierBMen = Tier(menB, 2)
        TierCMen = Tier(menC, 1)
        TierSetter = Tier(setter, 3)
        TierAWomen = Tier(womenA, 2)
        TierBWomen = Tier(womenB, 1)
        TierCWomen = Tier(womenC, 1)

        players = [TierAMen, TierBMen, TierCMen, TierSetter, TierAWomen, TierBWomen, TierCWomen]
        total_teams = int((len(menA)+len(menB)+len(menC)+len(womenA)+len(womenB)+len(womenC)+len(setter))/6)
        for i in range(total_teams):
            team = create_fixture(players)
            teams.append(team)

    for index, team in enumerate(teams):
        print(f"Team {index+1} : (points value at: {team.total_points})")
        print(team.members)
        print("\n")

    # Export teams to Excel with grouped formatting
    excel_file = '04_01_2026_Fixtures.xlsx'
    wb = Workbook()
    ws = wb.active
    ws.title = "All Teams"
    
    def header_cell(mcells, h1, text, team_nums, row, col, team_data):
        """
        Create a merged header cell and add team data below it.
        
        Args:
            mcells: Cell range to merge (e.g., 'B5:D5')
            h1: Header cell reference (e.g., 'B5')
            text: Header text (e.g., 'Group 1')
            team_nums: List of team numbers for column headers
            row: Starting row for column headers
            col: Starting column
            team_data: List of teams to display
        """
        ws.merge_cells(mcells)
        ws[h1] = text
        ws[h1].font = Font(bold=True, size=12)
        ws[h1].alignment = Alignment(horizontal='center')

        # Add column headers
        headers = [""] + [f"Team {num}" for num in team_nums]
        for count, header in enumerate(headers):
            cell = ws.cell(row=row, column=col + count)
            cell.value = header
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Add team data below headers
        max_players = max(len(team.members) for team in team_data) if team_data else 0
        
        for player_idx in range(max_players):
            ws.cell(row=row + 1 + player_idx, column=col).value = f"{player_idx + 1}"
            ws.cell(row=row + 1 + player_idx, column=col).font = Font(bold=True)
            ws.cell(row=row + 1 + player_idx, column=col).alignment = Alignment(horizontal='center')
            
            for team_idx, team in enumerate(team_data):
                if player_idx < len(team.members):
                    cell = ws.cell(row=row + 1 + player_idx, column=col + 1 + team_idx)
                    cell.value = team.members[player_idx]
                    cell.alignment = Alignment(horizontal='center')
    
    # Group teams by pairs and create formatted sections
    teams_per_group = 2
    groups = [teams[i:i + teams_per_group] for i in range(0, len(teams), teams_per_group)]
    
    max_players = max(len(team.members) for team in teams) if teams else 6
    row_spacing = max_players + 3  # Add space for header, column headers, and a blank row
    
    for group_idx, group in enumerate(groups):
        row = 2 + (group_idx // 2) * row_spacing
        col = 2 + (group_idx % 2) * 4
        group_num = group_idx + 1
        team_nums = [group_idx * teams_per_group + 1 + i for i in range(len(group))]
        
        cell_ref = f"{chr(64 + col)}{row}:{chr(64 + col + len(group))}{row}"
        header_ref = f"{chr(64 + col)}{row}"
        
        header_cell(cell_ref, header_ref, f"Group {group_num}", team_nums, row + 1, col, group)
    
    wb.save(excel_file)
    print(f"\nTeams exported to {excel_file}")

main()
import random, math, io
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


def create_balanced_teams(players_dict, setters_list, num_teams=4):
    """
    Create balanced teams with constraints:
    - Each team has exactly 1 setter
    - Women distributed equally (should have same number of women per team)
    - Points per team should be balanced
    """
    teams = [Team([], 0) for _ in range(num_teams)]
    
    # Track women count per team
    women_per_team = [0] * num_teams
    
    # Step 1: Distribute setters (1 per team)
    setter_pool = setters_list.copy()
    random.shuffle(setter_pool)
    
    for team_idx, setter_name in enumerate(setter_pool[:num_teams]):
        # Find which tier this setter belongs to and get their points
        setter_points = 0
        is_woman = False
        for tier_name, tier_obj in players_dict.items():
            if setter_name in tier_obj.members:
                setter_points = tier_obj.points
                # Check if this setter is a woman BEFORE removing
                if tier_name in ['womenA', 'womenB']:
                    is_woman = True
                # Remove from tier to avoid duplication
                tier_obj.members = tier_obj.members[tier_obj.members != setter_name]
                break
        
        teams[team_idx].members = np.append(teams[team_idx].members, setter_name)
        teams[team_idx].total_points += setter_points
        
        # Track if setter is a woman
        if is_woman:
            women_per_team[team_idx] += 1
    
    # Step 2: Distribute women equally (prioritize equal distribution)
    women_tiers = ['womenA', 'womenB']
    for tier_name in women_tiers:
        if tier_name not in players_dict:
            continue
        
        tier = players_dict[tier_name]
        while len(tier.members) > 0:
            # Find team with least women
            team_idx = women_per_team.index(min(women_per_team))
            
            # Pick a woman from this tier
            chosen = luckydraw(tier)
            if chosen is None:
                break
            
            teams[team_idx].members = np.append(teams[team_idx].members, chosen)
            teams[team_idx].total_points += tier.points
            tier.members = tier.members[tier.members != chosen]
            women_per_team[team_idx] += 1
    
    # Step 3: Fill remaining spots trying to balance points
    # Sort teams by current points (ascending) to fill lower-point teams first
    remaining_tiers = ['menA', 'menB', 'menC', 'wildcard']
    
    while True:
        # Check if all teams are full (6 players each)
        if all(len(team.members) >= 6 for team in teams):
            break
        
        # Find available tiers
        available_tiers = [tier_name for tier_name in remaining_tiers 
                          if tier_name in players_dict and len(players_dict[tier_name].members) > 0]
        
        if not available_tiers:
            break
        
        # Find team with lowest points that's not full
        team_idx = min([i for i, team in enumerate(teams) if len(team.members) < 6],
                      key=lambda i: teams[i].total_points)
        
        # Try to pick from a tier that balances points
        # Prefer higher-point tiers for lower-point teams
        current_avg_points = sum(t.total_points for t in teams) / num_teams
        
        if teams[team_idx].total_points < current_avg_points:
            # Pick from higher-point tier
            tier_name = max(available_tiers, key=lambda t: players_dict[t].points)
        else:
            # Pick from lower-point tier
            tier_name = min(available_tiers, key=lambda t: players_dict[t].points)
        
        tier = players_dict[tier_name]
        chosen = luckydraw(tier)
        
        if chosen is None:
            continue
        
        teams[team_idx].members = np.append(teams[team_idx].members, chosen)
        teams[team_idx].total_points += tier.points
        tier.members = tier.members[tier.members != chosen]
    
    return teams

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
    Column E: women tier (A/B)
    Column G: setter names
    
    New tiering system:
    - Men A - 4pt
    - Men B - 3pt
    - Women A - 3pt
    - Men C - 2pt
    - Women B - 2pt
    - Wildcard - 1pt
    """
    wb = load_workbook(excel_file)
    ws = wb.active
    
    menA, menB, menC = [], [], []
    womenA, womenB = [], []
    wildcard = []
    setter = []
    
    # Read men (columns A and B)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=1).value  # Column A
        tier = ws.cell(row=row, column=2).value  # Column B
        if name:
            name = str(name).strip()  # Clean up whitespace
            if tier == 'A':
                menA.append(name)
            elif tier == 'B':
                menB.append(name)
            elif tier == 'C':
                menC.append(name)
            elif tier == 'Wildcard' or tier == 'W':
                wildcard.append(name)
    
    # Read women (columns D and E)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=4).value  # Column D
        tier = ws.cell(row=row, column=5).value  # Column E
        if name:
            name = str(name).strip()  # Clean up whitespace
            if tier == 'A':
                womenA.append(name)
            elif tier == 'B':
                womenB.append(name)
            elif tier == 'Wildcard' or tier == 'W':
                wildcard.append(name)
    
    # Read setter (column G)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=7).value  # Column G
        if name:
            name = str(name).strip()  # Clean up whitespace
            setter.append(name)
    
    wb.close()
    
    return {
        'menA': menA,
        'menB': menB,
        'menC': menC,
        'womenA': womenA,
        'womenB': womenB,
        'wildcard': wildcard,
        'setter': setter
    }

def _build_player_info(tier_data):
    player_info = {}
    for name in tier_data['menA']:
        player_info[name] = {'gender': 'men', 'tier': 'A'}
    for name in tier_data['menB']:
        player_info[name] = {'gender': 'men', 'tier': 'B'}
    for name in tier_data['menC']:
        player_info[name] = {'gender': 'men', 'tier': 'C'}
    for name in tier_data['womenA']:
        player_info[name] = {'gender': 'women', 'tier': 'A'}
    for name in tier_data['womenB']:
        player_info[name] = {'gender': 'women', 'tier': 'B'}
    for name in tier_data['wildcard']:
        player_info[name] = {'gender': 'wildcard', 'tier': 'W'}
    for setter_name in tier_data['setter']:
        if setter_name not in player_info:
            player_info[setter_name] = {'gender': 'wildcard', 'tier': 'W'}
    return player_info


def _generate_all_teams(tier_data, num_teams=4, min_groups=10):
    all_teams = []
    batches_needed = math.ceil(min_groups / 2)

    for batch_num in range(batches_needed):
        players_dict = {
            'menA': Tier(tier_data['menA'].copy(), 4),
            'menB': Tier(tier_data['menB'].copy(), 3),
            'menC': Tier(tier_data['menC'].copy(), 2),
            'womenA': Tier(tier_data['womenA'].copy(), 3),
            'womenB': Tier(tier_data['womenB'].copy(), 2),
            'wildcard': Tier(tier_data['wildcard'].copy(), 1),
        }
        setter = tier_data['setter'].copy()
        teams = create_balanced_teams(players_dict, setter, num_teams)
        all_teams.extend(teams)

    return all_teams


def _export_teams_to_excel(all_teams, player_info):
    wb = Workbook()
    ws = wb.active
    ws.title = "All Teams"

    colors = {
        'menA': 'b0e0e6',
        'menB': 'afeeee',
        'menC': 'e0ffff',
        'womenA': 'ffd6dc',
        'womenB': 'ffe6e9',
        'wildcard': 'E6E6FA'
    }

    def get_player_color(player_name):
        if player_name not in player_info:
            return None
        info = player_info[player_name]
        # Color coding currently disabled in original code
        return None

    def header_cell(mcells, h1, text, team_nums, row, col, team_data):
        ws.merge_cells(mcells)
        ws[h1] = text
        ws[h1].font = Font(bold=True, size=12)
        ws[h1].alignment = Alignment(horizontal='center')

        headers = [""] + [f"Team {num}" for i, num in enumerate(team_nums)]
        for count, header in enumerate(headers):
            cell = ws.cell(row=row, column=col + count)
            cell.value = header
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', wrap_text=True)

        max_players = max(len(team.members) for team in team_data) if team_data else 0

        for player_idx in range(max_players):
            ws.cell(row=row + 1 + player_idx, column=col).value = f"{player_idx + 1}"
            ws.cell(row=row + 1 + player_idx, column=col).font = Font(bold=True)
            ws.cell(row=row + 1 + player_idx, column=col).alignment = Alignment(horizontal='center')

            for team_idx, team in enumerate(team_data):
                if player_idx < len(team.members):
                    cell = ws.cell(row=row + 1 + player_idx, column=col + 1 + team_idx)
                    player_name = team.members[player_idx]
                    cell.value = player_name
                    cell.alignment = Alignment(horizontal='center')

                    color = get_player_color(player_name)
                    if color:
                        cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')

    teams_per_group = 2
    groups = [all_teams[i:i + teams_per_group] for i in range(0, len(all_teams), teams_per_group)]

    max_players = max(len(team.members) for team in all_teams) if all_teams else 6
    row_spacing = max_players + 3

    for group_idx, group in enumerate(groups):
        row = 2 + (group_idx // 2) * row_spacing
        col = 2 + (group_idx % 2) * 4
        group_num = group_idx + 1
        team_nums = [group_idx * teams_per_group + 1 + i for i in range(len(group))]

        cell_ref = f"{chr(64 + col)}{row}:{chr(64 + col + len(group))}{row}"
        header_ref = f"{chr(64 + col)}{row}"

        header_cell(cell_ref, header_ref, f"Group {group_num}", team_nums, row + 1, col, group)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def generate_fixtures(excel_input, num_teams=4, min_groups=10):
    """
    Main entry point: accepts an Excel file (path or bytes), generates
    balanced team fixtures, and returns the output Excel file as bytes.
    """
    if isinstance(excel_input, (bytes, bytearray)):
        excel_input = io.BytesIO(excel_input)

    tier_data = read_tier_list(excel_input)
    player_info = _build_player_info(tier_data)
    all_teams = _generate_all_teams(tier_data, num_teams, min_groups)
    return _export_teams_to_excel(all_teams, player_info)


def main():
    tier_list_file = 'tier_list.xlsx'
    output_bytes = generate_fixtures(tier_list_file)

    output_file = 'Fixtures.xlsx'
    with open(output_file, 'wb') as f:
        f.write(output_bytes)
    print(f"Teams exported to {output_file}")


if __name__ == "__main__":
    main()
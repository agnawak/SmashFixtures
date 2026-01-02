import numpy as np

class Tier:
    def __init__(self, data, points):
        self.data_array = np.array(data, dtype=str)
        self.points = points

class Team:
    def __init__(self, members, total_points):
        self.members = members
        self.total_points = total_points

menA = ['man1', 'man2', 'man3', 'man4','man5' , 'man6']
TierAMen = Tier(menA, 3)
womenA = ['woman1', 'woman2', 'woman3', 'woman4','woman5' , 'woman6']
TierAWomen = Tier(womenA, 2)

arr = [TierAMen, TierAWomen]

print(arr[0].data_array[0])
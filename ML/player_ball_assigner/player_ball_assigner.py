import sys 
sys.path.append("../")
from utils.bbox_utils import get_center_of_bbox 

class Playerassigner():
    def __init__(self):
        self.max_player_ball_distance = 70 
        
    def assign_ball_to_player(self,players,ball_bbox):
        
import sys 
sys.path.append('../')
from utils.bbox_utils import get_center_of_bbox ,measure_distance


        
class Playerassigner:
    def __init__(self):
        self.max_player_ball_distance = 700  # Adjust threshold based on observed distances

    def assign_ball_to_player(self, players, ball_bbox):
        # Validate ball bounding box
        if not ball_bbox or len(ball_bbox) != 4:
            return -1

        ball_position = get_center_of_bbox(ball_bbox)
        if not ball_position:
            return -1

        # Initialize assignment variables
        assigned_player = -1
        minimum_distance = float('inf')

        # Iterate through players to find the closest one
        for player_id, player in players.items():
            player_bbox = player.get("bbox")
            if not player_bbox or len(player_bbox) != 4:
                continue

            # Calculate distances
            x1, y1, x2, y2 = player_bbox
            distance_left = measure_distance((x1, y2), ball_position)
            distance_right = measure_distance((x2, y2), ball_position)
            distance = min(distance_left, distance_right)

            # Assign player if within range and closer than the current closest player
            if distance < self.max_player_ball_distance and distance < minimum_distance:
                minimum_distance = distance
                assigned_player = player_id

        return assigned_player

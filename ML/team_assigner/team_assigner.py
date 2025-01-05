class Teamassigner:
    def __init__(self):
        pass 
    
    
    def assign_team_color(self,frame,player_detections):
        player_colors = []
        for _,player_detection in player_detections.items():
            bbox = player_detection["bbox"]
            player_color = self.get_player_color(frame,bbox)
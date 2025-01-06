class Speedanddistanceestimator():
    def __init__(self):
        self.frame_window = 5 
        self.frame_rate = 24 
        
        
    def add_speed_and_distance_to_tracks(self,tracks):
        for object , object_tracks in tracks.items():
            if object == 'ball' or object == 'referees' :
                continue
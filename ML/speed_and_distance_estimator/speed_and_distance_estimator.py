class Speedanddistanceestimator():
    def __init__(self):
        self.frame_window = 5 
        self.frame_rate = 24 
        
        
    def add_speed_and_distance_to_tracks(self,tracks):
        for object , object_tracks in tracks.items():
            if object == 'ball' or object == 'referees' :
                continue
            number_of_frames = len(object_tracks)
            for frame_num in range(0,number_of_frames,self.frame_window):
                
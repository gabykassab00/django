import sys
sys.path.append
from utils.bbox_utils import measure_distance

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
                last_frame  = min(frame_num+self.frame_window,number_of_frames)
                
            for track_id ,_ in object_tracks[frame_num].items():
                if track_id not in object_tracks[last_frame]:
                    continue
                
                start_position = object_tracks[frame_num][track_id]['position_transformed']
                end_position = object_tracks[last_frame][track_id]['position_transformed']
                
                
                if start_position is None or end_position is None:
                    continue
                
                distance_covered = measure_distance(start_position,end_position)
                time_elapsed = (last_frame-frame_num)/self.frame_rate
                speed_meter_per_second =distance_covered/time_elapsed
                speed_km_per_hour = speed_meter_per_second*3.6
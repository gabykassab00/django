
import sys
sys.path.append
from ML.utils.bbox_utils import measure_distance,get_foot_position
import cv2


class Speedanddistanceestimator():
    def __init__(self):
        self.frame_window = 5 
        self.frame_rate = 24 
        
        
    def add_speed_and_distance_to_tracks(self,tracks):
        
        total_distance = {} 
        
        
        
        for object , object_tracks in tracks.items():
            if object == 'ball' or object == 'referees' :
                continue
            number_of_frames = len(object_tracks)
            for frame_num in range(0,number_of_frames,self.frame_window):
                last_frame  = min(frame_num+self.frame_window,number_of_frames-1)
                
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
                    
                    if object not in total_distance:
                        total_distance[object] = {}
                        
                    if track_id not in total_distance[object]:
                        total_distance[object][track_id] = 0 
                        
                    total_distance[object][track_id] += distance_covered
                    
                    for frame_num_batch in range(frame_num,last_frame):
                        if track_id not in tracks[object][frame_num_batch]:
                            continue
                        
                        tracks[object][frame_num_batch][track_id]['speed'] = speed_km_per_hour
                        tracks[object][frame_num_batch][track_id]['distance'] = total_distance[object][track_id]
                        


    def draw_speed_and_distance(self,frame,tracks):
        player_stats={} 
        
        output_frames = []
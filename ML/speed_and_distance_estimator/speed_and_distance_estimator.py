
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
                        


    def draw_speed_and_distance(self, frames, tracks):
        player_stats = {"team1": {}, "team2": {}}  
        
        output_frames = []
        for frame_num, frame in enumerate(frames):
            for object, object_tracks in tracks.items():
                if object == "ball" or object == "referees":
                    continue
                for track_id, track_info in object_tracks[frame_num].items():
                    if "speed" in track_info:
                        speed = track_info.get("speed", None)
                        distance = track_info.get("distance", None)
                        if speed is None or distance is None:
                            continue
                        
                        bbox = track_info["bbox"]
                        position = get_foot_position(bbox)
                        position = list(position)
                        position[1] += 40
                        position = tuple(map(int, position))
                        
                        # Determine the player's team
                        team = track_info.get("team", None)  
                        if team is None:
                            print(f"Player {track_id} has no team assigned.")
                            continue
                        
                        # Initialize stats for the player if not present
                        if track_id not in player_stats[f"team{team}"]:
                            player_stats[f"team{team}"][track_id] = {"total_speed": 0, "speed_count": 0, "total_distance": 0}
                        
                        # Update stats
                        player_stats[f"team{team}"][track_id]["total_speed"] += speed
                        player_stats[f"team{team}"][track_id]["speed_count"] += 1
                        player_stats[f"team{team}"][track_id]["total_distance"] = distance
            
            output_frames.append(frame)
        
        # Log stats for each team
        print("\nTeam 1 Stats:")
        for player_id, stats in player_stats["team1"].items():
            average_speed = stats["total_speed"] / stats["speed_count"] if stats["speed_count"] > 0 else 0
            total_distance = stats["total_distance"]
            print(f"Player {player_id}: Average Speed: {average_speed:.2f} km/h, Total Distance: {total_distance:.2f} m")
        
        print("\nTeam 2 Stats:")
        for player_id, stats in player_stats["team2"].items():
            average_speed = stats["total_speed"] / stats["speed_count"] if stats["speed_count"] > 0 else 0
            total_distance = stats["total_distance"]
            print(f"Player {player_id}: Average Speed: {average_speed:.2f} km/h, Total Distance: {total_distance:.2f} m")
        
        return output_frames
   



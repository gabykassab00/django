from ultralytics import YOLO
import supervision as sv
import pickle
import os
import sys 
sys.path.append('../')
from ML.utils.bbox_utils import get_center_of_bbox,get_bbox_width,get_foot_position
import cv2
import numpy as np
import pandas as pd



class Tracker:
    def __init__(self,model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        
        
    def add_position_to_tracks(self,tracks):
        for object , object_tracks in tracks.items():
            for frame_num , track in enumerate(object_tracks):
                for track_id,track_info in track.items():
                    bbox = track_info['bbox']
                    if object == 'ball':
                        position = get_center_of_bbox(bbox)
                    else :
                        position = get_foot_position(bbox)
                    tracks[object][frame_num][track_id]['position'] = position
                        
        
    def interpolate_ball_positions(self,ball_positions):
        ball_positions = [ x.get(1,{}).get('bbox',[]) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions,columns=['x1','y1','x2','y2'])
        
        #interpolate missing values 
        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill() 
        
        ball_positions = [{1:{"bbox":x}} for x in df_ball_positions.to_numpy().tolist()]

        
        
        return ball_positions
        
    def detect_frames(self,frames):
        batch_size = 20 
        detections =[]
        for i in range(0,len(frames),batch_size):
           detections_batch = self.model.predict(frames[i:i+batch_size],conf=0.1)
           detections += detections_batch
        return detections
       
    
    def get_object_tracks(self,frames,read_from_stub = False ,stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f :
                tracks = pickle.load(f)
            return tracks
        
        
        detections=self.detect_frames(frames)
        
        tracks ={
           "players":[] ,
           "referees":[],
           "ball":[],
        }
        
        
        for frame_num , detection in enumerate(detections):
            cls_names = detection.names
            cls_names_inv = {value:key for key,value in cls_names.items()}
            #convert to supervision detection format 
            detection_supervision = sv.Detections.from_ultralytics(detection)
            
            
            #convert goalkeeper to player object 
            
            for object_ind , class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]
                    
                    
            #track object
            detection_with_tracks = self.tracker.update_with_detections(detection_supervision)
            
            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})
            
            for frame_detection in detection_with_tracks:
                bbox = frame_detection[0].tolist()
                class_id = frame_detection[3]
                track_id = frame_detection[4]
                
                if class_id == cls_names_inv['player']:
                    tracks["players"][frame_num][track_id] = {"bbox":bbox}
                
                if class_id == cls_names_inv['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox":bbox}
                    
            for frame_detection in detection_supervision:
                bbox = frame_detection[0].tolist()
                class_id = frame_detection[3]
                
                if class_id == cls_names_inv["ball"]:
                    tracks["ball"][frame_num][1] ={"bbox":bbox}
                    
        if stub_path is not None:
            with open(stub_path,'wb')as f :
                pickle.dump(tracks,f)
            
            
        return  tracks        
        
    def draw_ellipse(self,frame,bbox,color,track_id=None):
        y2 = int(bbox[3])
        x_center,_ = get_center_of_bbox(bbox)
        width= get_bbox_width(bbox)
        
        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width),int(0.35*width)),
            angle=0.0,
            startAngle = -45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4
        )
        
        rectangle_width = 40 
        rectangle_height = 20 
        x1_rect = x_center - rectangle_height//2
        x2_rect = x_center + rectangle_height//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15
        
        if track_id is not None:
            cv2.rectangle(frame,(int(x1_rect),int(y1_rect)),(int(x2_rect),int(y2_rect)),color,cv2.FILLED)
            
            x1_text = x1_rect +12 
            if track_id > 99 :
                x1_text -=10
            cv2.putText(frame,f"{track_id}",(int(x1_text),int(y1_rect+15)),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2)
        
        return frame
    
    
    
    def draw_triangle(self,frame,bbox,color):
        y=int(bbox[1])
        x,_= get_center_of_bbox(bbox)
        
        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame,[triangle_points],0,color,cv2.FILLED)
        cv2.drawContours(frame,[triangle_points],0,(0,0,0),2)
        
        return frame 
        
        

    
    
    def draw_team_ball_control(self, frame, frame_num, team_ball_control):
        # Debugging: Check lengths and frame number

        # Draw a semi-transparent rectangle
        overlay = frame.copy()
        cv2.rectangle(overlay, (1350, 850), (1900, 970), (255, 255, 255), -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Get the team ball control up to the current frame
        team_ball_control_till_frame = team_ball_control[:frame_num + 1]

        # Calculate the number of frames each team had the ball
        team_1_num_frames = team_ball_control_till_frame[team_ball_control_till_frame == 1].shape[0]
        team_2_num_frames = team_ball_control_till_frame[team_ball_control_till_frame == 2].shape[0]

        # Handle division by zero
        total_frames = team_1_num_frames + team_2_num_frames
        if total_frames == 0:
            team_1 = 0.0
            team_2 = 0.0
        else:
            team_1 = team_1_num_frames / total_frames
            team_2 = team_2_num_frames / total_frames

        # Draw text on the frame
        # cv2.putText(frame, f"team 1 ball control :{team_1*100:.2f}%", (1400, 900), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        # cv2.putText(frame, f"team 2 ball control :{team_2*100:.2f}%", (1400, 950), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

        # Print ball control for the current frame

        # Debug: Check if last frame is reached
        if frame_num == len(team_ball_control) - 2:
            print(f"Last Frame Detected: {frame_num}")
            avg_team_1_control = (team_ball_control == 1).sum() / len(team_ball_control) * 100
            avg_team_2_control = (team_ball_control == 2).sum() / len(team_ball_control) * 100
            print(f"Average Team 1 Ball Control: {avg_team_1_control:.2f}%")
            print(f"Average Team 2 Ball Control: {avg_team_2_control:.2f}%")

        return frame


        
    def draw_annotations(self,video_frames,tracks,team_ball_control):
        output_video_frames = []
        for frame_num,frame in enumerate(video_frames):
            frame = frame.copy()
            
            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict=tracks["referees"][frame_num]
            
            #draw players 
            
            for track_id , player in player_dict.items():
                color = player.get("team_color",(0,0,255))
                frame= self.draw_ellipse(frame,player["bbox"],color,track_id)
                
                if player.get('has_ball',False):
                    frame = self.draw_triangle(frame,player["bbox"],(0,0,255))
                
                
            #draw referee 
            
            for _, referee in referee_dict.items():
                frame=self.draw_ellipse(frame,referee["bbox"],(0,255,255))
                
                
            #draw ball
            
            for track_id,ball in ball_dict.items():
                frame = self.draw_triangle(frame,ball["bbox"],(0,255,0))
                
            #draw team ball control 
            frame = self.draw_team_ball_control(frame,frame_num,team_ball_control)
                
            output_video_frames.append(frame)
            
        return output_video_frames
    
    
 
 
 
    def track_passes(self, tracks, team_assigner, video_frames):
        passes = {"team1": [], "team2": []}
        previous_possession = None
        possession_threshold = 50  


        for frame_num, player_tracks in enumerate(tracks["players"]):

            ball_tracks = tracks["ball"][frame_num]

            if not ball_tracks or 1 not in ball_tracks:
                continue

            # Get ball position
            ball_position = ball_tracks[1].get("position", get_center_of_bbox(ball_tracks[1]["bbox"]))

            closest_player_id, closest_distance = None, float("inf")

            # Find the closest player to the ball
            for player_id, player_data in player_tracks.items():
                player_position = player_data["position"]
                frame = video_frames[frame_num]
                player_bbox = player_data["bbox"]

                # Get the player's team using Teamassigner
                team = team_assigner.get_player_team(frame, player_bbox, player_id)
                player_data["team"] = team  # Update team in player data

                distance = np.linalg.norm(np.array(ball_position) - np.array(player_position))
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player_id = player_id


            # Check for possession change
            if previous_possession is not None:
                if previous_possession not in player_tracks:
                    previous_possession = None
                    continue

                previous_player_position = player_tracks[previous_possession]["position"]
                ball_movement = np.linalg.norm(np.array(previous_player_position) - np.array(ball_position))

                if closest_player_id != previous_possession and ball_movement > possession_threshold:
                    # Pass detected
                    pass_distance = np.linalg.norm(np.array(previous_player_position) - np.array(ball_position))
                    passer_team = player_tracks[previous_possession].get("team", "unknown")

                    pass_event = {
                        "frame": frame_num,
                        "passer": previous_possession,
                        "receiver": closest_player_id,
                        "distance": pass_distance,
                    }

                    # Assign pass to the corresponding team
                    if passer_team == 1:
                        passes["team1"].append(pass_event)
                    elif passer_team == 2:
                        passes["team2"].append(pass_event)
                    else:
                        print("Passer's team is unknown. Pass not added.")

            # Update possession
            previous_possession = closest_player_id


        return passes
 





















    
    





    
    



























from utils._init_ import read_video,save_video
from trackers._init_ import Tracker
import cv2
from team_assigner._init_ import Teamassigner
from player_ball_assigner._init_ import Playerassigner
import numpy as np
from camera_movement_estimator._init_ import Cameramovement


def main():
    #read video
    video_frames = read_video('ML/input_videos/v.mp4')
    
    
    #initialize tracker
    
    tracker = Tracker('ML/models/best1.pt')
    
    tracks = tracker.get_object_tracks(video_frames,read_from_stub=True,stub_path='ML/stubs/track_stubs.pkl')
    
    
    #get object positions
    tracker.add_position_to_tracks(tracks)
    
    
    #camera movement estimator 
    
    camera_movement_estimator = Cameramovement(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,read_from_stub=False,stub_path='ML/stubs/camera_movement_stub.pkl')
    
    
    
    #inteprolate ball positons 
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    
    #assign player teams 
    
    team_assigner = Teamassigner()
    team_assigner.assign_team_color(video_frames[0],tracks['players'][0])
    
    for frame_num , player_track in enumerate(tracks['players']):
        for player_id , track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num],track['bbox'],player_id)

            tracks['players'][frame_num][player_id]['team'] = team 
            tracks['players'][frame_num][player_id]['team_color']= team_assigner.team_colors[team]
            
            
    #assign ball aquisition 
    
    player_assigner = Playerassigner()
    team_ball_control =[-1]
    for frame_num , player_track in enumerate(tracks['players']):
        ball_bbox = tracks['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track,ball_bbox)
        
        if assigned_player != -1 :
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team'])
            
        else :
            team_ball_control.append(team_ball_control[-1])
    team_ball_control = np.array(team_ball_control)

    
    
    # #save cropped image of a player
    # for track_id,player in tracks['players'][0].items():
    #     bbox = player['bbox']
    #     frame = video_frames[0]
        
    #     #cropp bbox from frame
    #     cropped_image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
        
    #     #save cropped image 
        
    #     cv2.imwrite(f'ML/output_videos/cropped_img.jpg',cropped_image)
    #     break        
    
    #draw output 
    
    #draw object tracks 
    output_video_frames = tracker.draw_annotations(video_frames,tracks,team_ball_control)
    
    
    #draw camera movement 
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames,camera_movement_per_frame)
    
    #save video
    save_video(output_video_frames,'ML/output_videos/video_result.avi')
    
if __name__ == "__main__":
    main() 
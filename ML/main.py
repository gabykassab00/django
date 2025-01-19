
import os
import sys
import base64

# Get the directory containing `ML` and add it to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ML.utils.video_utils import read_video,save_video
from ML.trackers.tracker import Tracker
import cv2
from ML.team_assigner.team_assigner import Teamassigner
from ML.player_ball_assigner.player_ball_assigner import Playerassigner
import numpy as np
from ML.camera_movement_estimator.camera_movement_estimator import Cameramovement
from ML.view_transformer.view_transformer import Viewtransformer
from ML.speed_and_distance_estimator.speed_and_distance_estimator import Speedanddistanceestimator
from io import BytesIO

def main(video_path):
    
    print(f"Video Path Received: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File not found at: {video_path}")

    print(f"Processing video: {video_path}")
    
    
    
    
    #read video
    # video_frames = read_video('ML/input_videos/v.mp4')
    video_frames = read_video(video_path)
    
    
    #initialize tracker
    
    tracker = Tracker('ML/models/best10.pt')
    
    tracks = tracker.get_object_tracks(video_frames,read_from_stub=False,stub_path='ML/stubs/track_stubs.pkl')
    
    
    
    #get object positions
    tracker.add_position_to_tracks(tracks)
    
    
    #camera movement estimator 
    
    camera_movement_estimator = Cameramovement(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,read_from_stub=False,stub_path='ML/stubs/camera_movement_stub.pkl')
    
    
    camera_movement_estimator.adjust_positons_to_the_tracks(tracks,camera_movement_per_frame)
    
    
    
    #view transformer 
    view_transformer = Viewtransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    
    
    #inteprolate ball positons 
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    
    #speed and distance estimator 
    
    speed_and_distance_estimator = Speedanddistanceestimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)
    
    
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
    
    
    passes = tracker.track_passes(tracks,team_assigner,video_frames)
    # Print only the players who made passes
    # Initialize dictionaries to count passes
    passer_totals = {"team1": {}, "team2": {}}
    total_passes_per_team = {"team1": 0, "team2": 0}  

    # Count passes for each passer
    for team, team_passes in passes.items():
        for pass_event in team_passes:
            passer = pass_event['passer']
            if passer in passer_totals[team]:
                passer_totals[team][passer] += 1  
            else:
                passer_totals[team][passer] = 1  
            
            total_passes_per_team[team] += 1  

    # Print Passers and Total Passes
    print("\nPassers and Total Passes:")
    for team, team_passers in passer_totals.items():
        print(f"\n{team}:")
        for passer, total_passes in team_passers.items():
            print(f"Passer: {passer}, Total Passes: {total_passes}")

    # Print Total Passes for Each Team
    print("\nTotal Passes for Each Team:")
    for team, total_passes in total_passes_per_team.items():
        print(f"{team}: {total_passes} passes")


    #     #save cropped image 
    avg_team_1_control = (team_ball_control == 1).sum() / len(team_ball_control) * 100
    avg_team_2_control = (team_ball_control == 2).sum() / len(team_ball_control) * 100
    #cv2.imwrite(f'ML/output_videos/cropped_img.jpg',cropped_image)
    # Collect average speed and total distance stats
    player_stats = {"team1": {}, "team2": {}}
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            speed = track.get("speed", None)
            distance = track.get("distance", None)
            team = track.get("team", None)

            if speed is None or distance is None:
                print(f"Frame {frame_num}: Player {player_id} missing speed or distance")
                continue

            if team is None:
                print(f"Frame {frame_num}: Player {player_id} missing team assignment")
                continue

            print(f"Frame {frame_num}: Player {player_id} | Team {team} | Speed: {speed} km/h | Distance: {distance} m")

            team_key = f"team{team}"

            if player_id not in player_stats[team_key]:
                player_stats[team_key][player_id] = {"total_speed": 0, "speed_count": 0, "total_distance": 0}

            player_stats[team_key][player_id]["total_speed"] += speed
            player_stats[team_key][player_id]["speed_count"] += 1
            player_stats[team_key][player_id]["total_distance"] = distance

    # Prepare team stats with average speed and total distance
    team_stats = {"team1": {}, "team2": {}}
    team_summary = {"team1": {}, "team2": {}}

    for team, players in player_stats.items():
        total_avg_speed = 0
        total_distance = 0
        player_count = len(players)

        for player_id, stats in players.items():
            average_speed = stats["total_speed"] / stats["speed_count"] if stats["speed_count"] > 0 else 0
            total_distance += stats["total_distance"]
            total_avg_speed += average_speed
            team_stats[team][player_id] = {
                "average_speed": average_speed,
                "total_distance": stats["total_distance"],
            }

        team_summary[team] = {
            "average_team_speed": total_avg_speed / player_count if player_count > 0 else 0,
            "total_team_distance": total_distance,
        }

    print("\nTeam Summaries:")
    for team, summary in team_summary.items():
        print(f"{team}: Average Speed: {summary['average_team_speed']:.2f} km/h, Total Distance: {summary['total_team_distance']:.2f} m")
    # here
    print("hayde lezem tchoufa",team_summary)
    
    #draw output 
    
    #draw object tracks 
    output_video_frames = tracker.draw_annotations(video_frames,tracks,team_ball_control)
    
    
    #draw camera movement 
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames,camera_movement_per_frame)
    
   
    #draw speed and distance 
    
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames,tracks)
   
    #save video
    save_video(output_video_frames,'ML/output_videos/video_result.avi')

    

    
    return {
        "passers_totals": passer_totals,
        "total_passes_per_team": total_passes_per_team,
        "team_ball_control": {
        "team1": avg_team_1_control,
        "team2": avg_team_2_control,
    },
        "team_stats": team_stats,  
        "team_summary": team_summary,

    }
    
    
    
    
    
    
if __name__ == "__main__":
    main() 












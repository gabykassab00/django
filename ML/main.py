from utils._init_ import read_video,save_video
from trackers._init_ import Tracker
import cv2
def main():
    #read video
    video_frames = read_video('ML/input_videos/v.mp4')
    
    
    #initialize tracker
    
    tracker = Tracker('ML/models/best1.pt')
    
    tracks = tracker.get_object_tracks(video_frames,read_from_stub=True,stub_path='ML/stubs/track_stubs.pkl')
    
    
    #save cropped image of a player
    for track_id,player in tracks['players'][0].items():
        bbox = player['bbox']
        frame = video_frames[0]
        
    #cropp bbox from frame
    cropped_image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
    
    #save cropped image 
    
    cv2.imwrite(f'ML/output_videos/cropped_img.jpg',cropped_image)
    break        
    
    #draw output 
    
    #draw object tracks 
    output_video_frames = tracker.draw_annotations(video_frames,tracks)
    
    #save video
    save_video(output_video_frames,'ML/output_videos/video_result.avi')
    
if __name__ == "__main__":
    main() 
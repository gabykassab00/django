from utils._init_ import read_video,save_video

def main():
    #read video
    video_frames = read_video('ML/input_videos/v.mp4')
    
    #save video
    save_video(video_frames,'ML/output_videos/video_result.avi')
    
if __name__ == "__main__":
    main() 
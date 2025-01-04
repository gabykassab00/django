from utils._init_ import read_video,save_video

def main():
    #read video
    video_frames = read_video('input_videos/input_videos/v.mp4')
    
    #save video
    save_video(video_frames,'output_videos/output_video.avi')
    
if __name__ == "_main_":
    main()
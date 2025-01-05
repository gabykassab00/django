import pickle
import cv2
import numpy as np
class Cameramovement():
    def __init__(self,frame):
        
        self.lk_params = dict (
            winSize = (15,15),
            maxLevel = 2 ,
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TermCriteria_COUNT,10,0.83)
        )
        
        
        first_frame_grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        mask_features = np.zeros_like(first_frame_grayscale)
        mask_features[:,0:20] = 1 
        mask_features[:,900:1050] = 1 
        
        self.features = dict(
            maxCorners = 100 ,
            qualityLevel = 0.3 ,
            minDistance = 3 ,
            blockSize = 7 ,
            mask= mask_features
        )
    
    def get_camera_movement(self,frames,read_from_stub=False,stub_path=None):
        #read from stub 
        
        camera_movement = [[0,0]*len(frames)]
        
        old_gray = cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray,**self.features)
        
        for frame_num in range(1,len(frames)):
            frame_gray = cv2.cvtColor(frames[frame_num],cv2.COLOR_BGR2GRAY)
            new_features,_,_ = cv2.calcOpticalFlowPyrLK(old_gray,frame_gray,old_features,None,**self.lk_params)
            
            max_distance = 0 
            camera_movement_x , camera_movement_y = 0,0 
            
            
            for i , (new,old) in enumerate(old_features,new_features):
                new_features_point =new.ravel()
                old_features_point = old.ravel()
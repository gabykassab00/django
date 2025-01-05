import pickle
import cv2
import numpy as np
class Cameramovement():
    def __init__(self,frame):
        first_frame_grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        mask_features = np.zeros_like(first_frame_grayscale)
        mask_features[:,0:20] = 1 
        mask_features[:,900:1050] = 1 
    
    def get_camera_movement(self,frames,read_from_stub=False,stub_path=None):
        #read from stub 
        
        camera_movement = [[0,0]*len(frames)]
        
        old_gray = cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray,)
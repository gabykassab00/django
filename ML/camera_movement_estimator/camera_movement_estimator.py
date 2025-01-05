import pickle
import cv2
class Cameramovement():
    def __init__(self,frame):
        pass
    
    def get_camera_movement(self,frames,read_from_stub=False,stub_path=None):
        #read from stub 
        
        camera_movement = [[0,0]*len(frames)]
        
        old_gray = cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY)
        old_features = cv2.goodFeaturesToTrack(old_gray,)
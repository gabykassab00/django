from ultralytics import YOLO

class Tracker:
    def __init__(self,model_path):
        self.model = YOLO(model_path)
        
    def detect_frames(self,frames):
       batch_size = 20 
       detections =[]
       
       detections =  self.model.predict(frames)
       
    
    def get_object_tracks(self,frames):
        
        detections
        
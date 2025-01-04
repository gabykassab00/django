from ultralytics import YOLO

class Tracker:
    def __init__(self,model_path):
        self.model = YOLO(model_path)
    
    def get_object_tracks(self,frames):
        
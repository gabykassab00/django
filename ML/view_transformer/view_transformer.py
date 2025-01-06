import numpy as np


class Viewtransformer:
    def __init__(self):
        court_width = 68 
        court_length = 23.32 
        
        
        self.pixel_vertices = np.array({
            [110,1035],
            [265,275],
            [1640,915]
        })
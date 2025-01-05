from sklearn.cluster import KMeans

class Teamassigner:
    def __init__(self):
        pass 
    
    def get_clustering_model(self,image):
        #reshape the image into 2d array 
        image_2d = image.reshape(-1,3)
        
        #perform k-means with 2 clusters 
        
        kmeans = KMeans(n_clusters=2,init="k-means++",n_init=1)
        kmeans.fit(image_2d)
        
        return kmeans
    
    
    def get_player_color(self,frame,bbox):
        image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
        
        top_half_image = image[0:int(image.shape[0]/2),:]
        
        #get clustering model 
        
        kmeans = self.get_clustering_model(top_half_image)
        
        #get the cluster labels for each pixel 
        
        labels= kmeans.labels_
        
        
    
    
    def assign_team_color(self,frame,player_detections):
        player_colors = []
        for _,player_detection in player_detections.items():
            bbox = player_detection["bbox"]
            player_color = self.get_player_color(frame,bbox)
from ultralytics import YOLO

model = YOLO('yolov8x')

results = model.predict('ML/input_videos/v.mp4',save=True,project='ML/runs',name='video_result1')
print(results[0])
for box in results[0].boxes:
    print(box)


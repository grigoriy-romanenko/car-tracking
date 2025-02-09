import cv2
import re
import geo
from collections import defaultdict
from ultralytics import YOLO
from config import *

class Metrics:
    def __init__(self, latitude, longitude, altitude, azimuth):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.azimuth = azimuth

class Detection:
    def __init__(self, x, y, frame_num):
        self.x = x
        self.y = y
        self.frame_num = frame_num

model = YOLO(model_file_path)
metrics = []
with open(metrics_file_path, 'r') as file:
    for frame in file.read().strip().split('\n\n'):
        m = re.findall(r'-?\d+.\d+', frame.split('\n')[-1])
        metrics.append(Metrics(float(m[5]), float(m[6]), float(m[8]), float(m[9])))
cap = cv2.VideoCapture(video_file_path)
tracks = defaultdict(lambda: [])
frame_num = 0
while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model.track(frame, device=device, imgsz=train_image_size, conf=track_confidence)
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            for box, track_id in zip(boxes, track_ids):
                x, y, w, h = box
                tracks[track_id].append(Detection(float(x), float(y), frame_num))
        frame_num += 1
    else:
        break
cap.release()
geo.make_map(metrics, tracks)

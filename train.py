import os
from ultralytics import YOLO
from config import device, dataset_file_path, train_image_size, model_file_path

if __name__ == '__main__':
    model = YOLO('yolo11n.pt').train(data=dataset_file_path, epochs=100, imgsz=train_image_size, device=device)
    os.replace(model.save_dir.joinpath('weights/best.pt'), model_file_path)

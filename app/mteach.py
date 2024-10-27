import cv2
import os
import json
from ultralytics import YOLO

# Инициализация модели
model = YOLO('best (1).pt')

def annotate_videos(video_paths, output_folder):
    # Папки для изображений и аннотаций
    images_folder = os.path.join(output_folder, "images")
    annotations_file = os.path.join(output_folder, "annotations.json")
    
    # Создаем папки, если они еще не существуют
    os.makedirs(images_folder, exist_ok=True)

    # Инициализация данных для JSON
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # Добавляем категории (предполагая, что классы начинаются с 0)
    num_classes = model.model.names  # Получаем названия классов из модели
    for class_id in range(len(num_classes)):
        coco_data["categories"].append({
            "id": class_id,
            "name": num_classes[class_id]
        })

    annotation_id = 0

    for video_path in video_paths:
        cap = cv2.VideoCapture(video_path)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        frame_id = 0
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Обработка каждого 100-го кадра
            if frame_count % 100 == 0:
                results = model.predict(frame)
                boxes = results[0].boxes  # Предсказания

                # Сохраняем информацию о кадре
                coco_data["images"].append({
                    "id": frame_id,
                    "file_name": f"{video_name}_frame{frame_id}.jpg",
                    "width": frame.shape[1],
                    "height": frame.shape[0]
                })

                # Сохраняем аннотации
                for box in boxes:
                    x_center, y_center, width, height = box.xywh[0].tolist()  # Преобразование координат в список
                    confidence = float(box.conf[0])  # Преобразуем в float
                    class_id = int(box.cls[0])  # Получаем целочисленный идентификатор класса

                    # Записываем аннотацию только при высокой уверенности
                    if confidence > 0.8:
                        annotation_id += 1
                        coco_data["annotations"].append({
                            "id": annotation_id,
                            "image_id": frame_id,
                            "category_id": class_id,
                            "bbox": [x_center - width / 2, y_center - height / 2, width, height],  # COCO требует [x, y, w, h]
                            "area": width * height,
                            "iscrowd": 0
                        })

                # Сохраняем кадр в папке изображений
                output_img_path = os.path.join(images_folder, f"{video_name}_frame{frame_id}.jpg")
                cv2.imwrite(output_img_path, frame)
                frame_id += 1

            frame_count += 1

        cap.release()

    # Сохраняем аннотации в JSON файл
    with open(annotations_file, "w") as f:
        json.dump(coco_data, f, indent=4)

# Пример использования
video_paths = ["1_1.mp4", "1_2.mp4", "1_3.mp4", "1_4.mp4", "1_5.mp4", "1_6.mp4"]
output_folder = "datasets/teach"
annotate_videos(video_paths, output_folder)
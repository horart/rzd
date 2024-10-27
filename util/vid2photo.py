# main.py

import cv2
import os

def extract_frames(video_path, output_folder):
   

    # Открываем видеофайл
    video = cv2.VideoCapture(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    # Проверка, что видео открылось успешно
    if not video.isOpened():
        print(f"Ошибка: Не удалось открыть видео {video_path}")
        return

    # Получаем количество кадров в секунду (FPS) и общее количество кадров
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Кадры для сохранения должны быть кратными 30 секундам
    frames_to_capture = int(30 * fps)
    
    current_frame = 0

    while True:
        # Читаем кадр
        ret, frame = video.read()

        if not ret:
            break
        
        # Проверяем, если кадр кратен 30 секундам
        if current_frame % frames_to_capture == 0:
            # Сохраняем кадр
            timestamp = int(current_frame / fps)
            frame_name = os.path.join(output_folder, f"frame_{video_name}_{timestamp}.png")
            cv2.imwrite(frame_name, frame)
            print(f"Сохранен кадр: {frame_name}")
        
        # Переходим к следующему кадру
        current_frame += 1

    # Освобождаем ресурсы
    video.release()
    print("Обработка завершена.")

# Пример использования
input_folder = "/home/crysingzz/Desktop/rzhd2_dataset"
output_folder = "/home/crysingzz/Desktop/outputvideo"  # Папка для сохранения кадров
for filename in os.listdir(input_folder):
        video_path = os.path.join(input_folder, filename)
        extract_frames(video_path,output_folder)
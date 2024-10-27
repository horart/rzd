import torch

# Загрузка первой модели YOLO
model1 = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Загрузка второй модели YOLO
model2 = torch.hub.load('ultralytics/yolov5', 'yolov5m')  # или другая версия

import cv2

# Открываем видео
cap = cv2.VideoCapture('path_to_your_video.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Обработка кадра первой моделью
    results1 = model1(frame)
    # Обработка кадра второй моделью
    results2 = model2(frame)

    # Отображение результатов первой модели
    frame1 = results1.render()[0]

    # Отображение результатов второй модели
    frame2 = results2.render()[0]

    # Объединение результатов
    combined_frame = cv2.hconcat([frame1, frame2])  # Или cv2.vconcat для вертикального размещения

    # Отображение объединенного кадра
    cv2.imshow('YOLO Outputs', combined_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

out = cv2.VideoWriter('output_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))

# Внутри цикла, после объединения кадров:
out.write(combined_frame)

# Не забудьте освободить объект записи после завершения
out.release()

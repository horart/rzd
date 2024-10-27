from ultralytics import YOLO
import cv2
import fresh_cam
from opencv_gst_rtsp_server import OpenCVFrameRTSPServer
import threading
from flask import Flask
from flask import request
import mysql.connector as mysql
import datetime

# Путь к модели YOLO и доступ к камере
MODEL_PATH = 'yolo_actual2.pt'
CAMERA_URI = 'rtsp://localhost:8554/cam1'

# Интерфейсы для журнала и трекинга объектов
tracks_interface: dict
state_interface: str
tracks: dict
journal_interface: list = []

# Перевод текущей даты и текущего времени в строку
def get_date_timef():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Преобразование множества идентификаторов в строку
def to_string(s: set, d: dict):
    return ", ".join(f"{d[id]} (id={id})" for id in s)

# Поиск ближайшего трека к указанному объекту
def get_closest(rect, po):
    p = po[0]
    mnx = min(p[0], p[2])
    mxx = max(p[0], p[2])
    mny = min(p[1], p[3])
    mxy = max(p[1], p[3])
    px = (mnx+mxx)/2
    py = (mny+mxy)/2
    track_n = -1
    min_dist = float('+inf')
    for key, f in tracks.items():
        r_mnx = min(f[0], f[2])
        r_mxx = max(f[0], f[2])
        r_mny = min(f[1], f[3])
        r_mxy = max(f[1], f[3])
        dx = max(r_mnx - px, 0, px - r_mxx)
        dy = max(r_mny - py, 0, py - r_mxy)
        d = (dx**2 + dy**2)**(1/2)
        if d < min_dist:
            track_n = key
            min_dist = d
    return track_n

# Объявление карты объектов
map_= {}

# Запуск модели и вывод потока
def ai_bg():
    global map_
    global tracks_interface
    global state_interface
    global journal_interface
    model = YOLO(MODEL_PATH)
    cap = fresh_cam.FreshestFrame(cv2.VideoCapture(CAMERA_URI))

    _, frame = cap.read()
    fps = int(cap.capture.get(cv2.CAP_PROP_FPS))
    fps = fps if  60 > fps > 0 else 30
    duration = 1.0/fps
    height, width, channel = frame.shape

    server = OpenCVFrameRTSPServer(width=width, height=height, channel=channel, fps=fps, use_h265=True, port=8001)
    server.start_background()
    in_frame = set()

    while True:
        newm = {k: 0 for k in tracks}
        resp, frame = cap.read()
        res = model.track(frame, persist=True)
        
        annotated_frame = res[0].plot()
        img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        server.set_frame(img)
        for box in res[0].boxes:
            if (gc := get_closest(box, box.data)) != -1:
                if not gc in newm:
                    newm[gc] = 0
                newm[gc] += 1

        tracks_interface = newm
        print(tracks_interface)
        cv2.waitKey(50)

        current_frame_objects = set()
        names = res[0].names
        for obj in res[0].boxes:
            nc = int(obj.cls[0])
            curr_id = int(obj.id[0])
            current_frame_objects.add(curr_id)
            map_[curr_id] = names[nc]
        
        new_in = current_frame_objects - in_frame
        exited = in_frame - current_frame_objects
        in_frame.update(new_in)
        in_frame.difference_update(exited)

        date_time = get_date_timef()
        state_interface = "Сейчас в кадре: " + to_string(in_frame, map_)

        if new_in:
            s = "Вошли в кадр:\n" + "\n".join(f"{map_[id]} (id={id})" for id in new_in)
            print(f"{date_time}\n{s}\n{state_interface}\n")
            journal_interface.append(f"{date_time}: {s} {state_interface}\n")
        if exited:
            s = "Вышли из кадра:\n" + "\n".join(f"{map_[id]} (id={id})" for id in exited)
            print(f"{date_time}\n{s}\n{state_interface}\n")
            journal_interface.append(f"{date_time}: {s} {state_interface}\n")


# Инициализация Flask приложения и базы данных MySQL
app = Flask('helpdisp')
db = mysql.connect(port=32000, user="root", password="root", database="rzd")

@app.route('/get_trains')            
def get_trains():
    return {'tracks': tracks_interface, 'journal': ''.join(journal_interface[-10:]), 'state': state_interface}

@app.route('/new_tracks', methods=['POST'])
def new_tracks():
    global tracks
    data = request.get_json()
    tracks = {k: v for k, v in enumerate(data, 1)}
    with db.cursor() as cursor:
        cursor.execute('DELETE FROM tracks WHERE 1')
        cursor.executemany('INSERT INTO tracks (id, topx, topy, botx, boty) VALUES (%s, %s, %s, %s, %s)', [[i, *tracks[i]] for i in tracks])
        db.commit()

# Блок запуска приложения
if __name__ == '__main__':
    with db.cursor() as cursor:
        cursor.execute("SELECT id, topx, topy, botx, boty FROM tracks")
        tracks = {i[0]: i[1:] for i in cursor.fetchall()}
        tracks_interface = [0]*len(tracks)
    ai_thread = threading.Thread(target=ai_bg)
    ai_thread.start()
    app.run()

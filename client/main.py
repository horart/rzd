# main.py

import tkinter as tk
from tkinter import filedialog, Label, Entry, Frame, Text
from tkinter import ttk
from ultralytics import YOLO
import cv2
from PIL import Image, ImageTk
import datetime

old_list_obj = dict()
work = dict()
first = True
FILE_NAME = 'output.txt'
LEN_BLOCK = 8
cnt = 0
map_ = dict()

# Возвращение a - b (то что есть в a, но нет в b)
def sub(a: dict, b: dict):
    ans = dict()
    for key in a:
        tmp = a[key] - b.get(key, 0)
        if tmp > 0:
            ans[key] = tmp
    for key in b:
        if a.get(key, 0) == 0:
            ans[key] = b[key]
    return ans

# Запись событий в файл и обновление журанала
def write(s: str, key='a'):
    with open(FILE_NAME, key) as file:
        file.write(s + '\n')
    log_text.insert(tk.END, s + '\n')
    log_text.see(tk.END)

# Функции для обработки и форматирования данных
def fillDict(base: dict, new: dict):
    for key in new:
        base[key] = max(base.get(key, 0), new[key])

def to_string(s: set, d: dict):
    return ", ".join(f"{d[id]} (id={id})" for id in s)

def get_date_timef():
    return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

# Функции для обучения и трекинга
def train_model(data_path, model_path, epochs):
    model = YOLO(model_path)
    model.train(data=data_path, epochs=epochs)

def predict(source_path, model_path, video_label):
    global cap, in_frame
    if cap:
        cap.release()
        cap = None

    model = YOLO(model_path)
    cap = cv2.VideoCapture(source_path)
    in_frame = set()

    def process_frame():
        global first, old_list_obj, FILE_NAME, cnt, map_
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return

        results = model.track(source=frame, persist=True)
        current_frame_objects = set()
        names = results[0].names
        for obj in results[0].boxes:
            nc = int(obj.cls[0])
            curr_id = int(obj.id[0])
            current_frame_objects.add(curr_id)
            map_[curr_id] = names[nc]

        new_in = current_frame_objects - in_frame
        exited = in_frame - current_frame_objects
        in_frame.update(new_in)
        in_frame.difference_update(exited)

        date_time = get_date_timef()
        state = "Сейчас в кадре: " + to_string(in_frame, map_)

        if new_in:
            s = "Вошли в кадр:\n" + "\n".join(f"{map_[id]} (id={id})" for id in new_in)
            write(f"{date_time}\n{s}\n{state}\n")
        if exited:
            s = "Вышли из кадра:\n" + "\n".join(f"{map_[id]} (id={id})" for id in exited)
            write(f"{date_time}\n{s}\n{state}\n")

        annotated_frame = results[0].plot()
        img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
        video_label.after(10, process_frame)

    process_frame()

# Функции для обработки действий пользователя
def select_data_file():
    data_path.set(filedialog.askopenfilename(title="Выберите YAML файл данных"))

def select_model_file():
    model_path.set("best.pt")

def select_source_file():
    source_path.set("train-crane.mp4")

def start_training():
    train_model(data_path.get(), model_path.get(), int(epochs_entry.get()))

def start_prediction():
    if source_path.get() and model_path.get():
        predict(source_path.get(), model_path.get(), video_label)

def restart_prediction():
    if cap:
        cap.release()
    start_prediction()

# Настройка интерфейса
app = tk.Tk()
app.title("YOLO Training and Prediction Interface")
app.geometry("1400x800")
app.configure(bg="#4C4A44")

# Переменные для путей к файлам
data_path = tk.StringVar()
model_path = tk.StringVar()
source_path = tk.StringVar()
cap = None
in_frame = set()

# Цветовая схема и стили
BUTTON_BG = "#444444"
BUTTON_ACTIVE_BG = "#666666"
LABEL_BG = "#4C4A44"
LABEL_FG = "#FFFFFF"
FONT = ("Arial", 12)

# Настройка стилей
style = ttk.Style()
style.configure("ElegantButton.TButton", font=FONT, background=BUTTON_BG, padding=6, relief="flat")
style.map("ElegantButton.TButton", background=[("active", BUTTON_ACTIVE_BG)])

# Организация виджетов в Frame для стабильной компоновки
controls_frame = Frame(app, bg=LABEL_BG)
controls_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

Label(controls_frame, text="YAML файл данных:", font=FONT, bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=0, pady=5, sticky="w")
ttk.Button(controls_frame, text="Выбрать", command=select_data_file, style="ElegantButton.TButton").grid(row=0, column=1)
Label(controls_frame, textvariable=data_path, bg=LABEL_BG, font=FONT, fg=LABEL_FG).grid(row=0, column=2, sticky="w")

Label(controls_frame, text="Файл весов модели (.pt):", font=FONT, bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=0, pady=5, sticky="w")
ttk.Button(controls_frame, text="Выбрать", command=select_model_file, style="ElegantButton.TButton").grid(row=1, column=1)
Label(controls_frame, textvariable=model_path, bg=LABEL_BG, font=FONT, fg=LABEL_FG).grid(row=1, column=2, sticky="w")

Label(controls_frame, text="Файл для предсказания:", font=FONT, bg=LABEL_BG, fg=LABEL_FG).grid(row=2, column=0, pady=5, sticky="w")
ttk.Button(controls_frame, text="Выбрать", command=select_source_file, style="ElegantButton.TButton").grid(row=2, column=1)
Label(controls_frame, textvariable=source_path, bg=LABEL_BG, font=FONT, fg=LABEL_FG).grid(row=2, column=2, sticky="w")

Label(controls_frame, text="Количество эпох:", font=FONT, bg=LABEL_BG, fg=LABEL_FG).grid(row=3, column=0, pady=5, sticky="w")
epochs_entry = Entry(controls_frame, font=FONT)
epochs_entry.insert(0, "100")
epochs_entry.grid(row=3, column=1)

ttk.Button(controls_frame, text="Запустить обучение", command=start_training, style="ElegantButton.TButton").grid(row=4, column=0, pady=10, sticky="w")
ttk.Button(controls_frame, text="Запустить предсказание", command=start_prediction, style="ElegantButton.TButton").grid(row=5, column=0, pady=10, sticky="w")
ttk.Button(controls_frame, text="Перезапуск", command=restart_prediction, style="ElegantButton.TButton").grid(row=6, column=0, pady=10, sticky="w")
ttk.Button(controls_frame, text="Выход", command=app.quit, style="ElegantButton.TButton").grid(row=7, column=0, pady=10, sticky="w")

# Виджет для показа видео справа
video_label = Label(app, bg=LABEL_BG)
video_label.grid(row=0, column=1, rowspan=8, padx=10, pady=5)

# Виджет для показа данных из output.txt справа от видео
log_text = Text(app, width=50, height=40, bg=LABEL_BG, fg=LABEL_FG, font=FONT)
log_text.grid(row=0, column=2, rowspan=8, padx=10, pady=5)

app.mainloop()

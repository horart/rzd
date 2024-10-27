import tkinter as tk
import tkinter.messagebox as tkm
import cv2
from PIL import Image
from PIL import ImageTk
import requests

# Запуск приложения для разметки дорог
class MainWindow():
    def __init__(self, window, cap):
        self.window = window
        self.cap = cap
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.interval = 10
        self.canvas = tk.Canvas(self.window, width=960, height=1080)
        self.canvas.grid(row=0, column=0)
        root.after(self.interval, self.update_image)
        self.button = tk.Button()

        # Хранение координат выбранных дорог и их айди на экране
        self.select_rects = []
        self.rect_ids = []

    # Получение позиции мыши при начале выделения
    def get_mouse_posn(self, event):
        self.select_rects.append([event.x, event.y, event.x, event.y])
        self.rect_ids.append(self.canvas.create_rectangle(event.x, event.y, event.x, event.y,
                dash=(2,2), fill='black', outline='white'))
        self.select_rects[-1][0], self.select_rects[-1][1] = event.x, event.y

    # Отслеживание, а затем обновление выделенного сектора
    def update_sel_rect(self, event):
        self.select_rects[-1][2], self.select_rects[-1][3] = event.x, event.y
        self.canvas.coords(self.rect_ids[-1], self.select_rects[-1][0], self.select_rects[-1][1], self.select_rects[-1][2], self.select_rects[-1][3])
        print(self.select_rects[-1][0], self.select_rects[-1][1], self.select_rects[-1][2], self.select_rects[-1][3])
    def update_image(self):    
        self.OGimage = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.OGimage = Image.fromarray(self.OGimage) # to PIL format
        self.image = self.OGimage.resize((960, 1080), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        for idx, i in enumerate(self.select_rects):
            if idx < len(self.select_rects):
                self.rect_ids[idx] =  self.canvas.create_rectangle(i[0], i[1], i[2], i[3],
                    dash=(2,2), fill='black', outline='white')
            else:
                self.rect_ids.append(self.canvas.create_rectangle(i[0], i[1], i[2], i[3],
                    dash=(2,2), fill='black', outline='white'))
            self.canvas.create_text((i[0]+i[2])/2, (i[1]+i[3])/2, text=str(idx+1    ), fill="white", font=('Helvetica 15 bold'))
        self.window.after(self.interval, self.update_image)
        self.canvas.bind('<Button-1>', self.get_mouse_posn)
        self.canvas.bind('<B1-Motion>', self.update_sel_rect)
    def on_closing(self):
        global root
        if tkm.askyesno('Желаете сохранить?'):
            requests.post('http://localhost:5000/new_tracks', json=self.select_rects)
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    mw = MainWindow(root, cv2.VideoCapture("rtsp://localhost:8554/cam1"))
    root.protocol("WM_DELETE_WINDOW", mw.on_closing)
    root.mainloop()

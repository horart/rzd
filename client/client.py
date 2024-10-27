import tkinter as tk
import tkinter.messagebox as tkm
import cv2
from PIL import Image
from PIL import ImageTk
import requests

# Запуск приложения с заготовленным разрешением окна
class MainWindow():
    def __init__(self, window, cap):
        root.geometry('{}x{}'.format(1600, 1080))
        self.window = window
        self.cap = cap
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.interval = 10 # Interval in ms to get the latest frame
        self.canvas = tk.Canvas(self.window, width=960, height=1080)
        self.canvas.grid(row=0, column=0)
        # Обновляем кадр и журнал
        root.after(self.interval, self.update_image)
        tv = tk.StringVar()
        tv.set('Пути')
        tv2 = tk.StringVar()
        tv2.set('Журнал')
        self.blob = tk.StringVar()
        self.blob.set('')
        self.blob2 = tk.StringVar()
        self.blob2.set('')
        self.tframe = tk.Frame(self.window, background='black', height=1080, width=1400-960)
        self.tframe.grid(row=0, column=1)
        self.l1 = tk.Label(self.tframe, textvariable=tv, justify='center', font='Helvetica 30')
        self.l1.grid(row=0, columnspan=2)
        self.l2 = tk.Label(self.tframe, textvariable=self.blob, justify='left', font='Helvetica 20')
        self.l2.grid(row=1, columnspan=2)
        self.l3 = tk.Label(self.tframe, textvariable=tv2, justify='left', font='Helvetica 30')
        self.l3.grid(row=2, columnspan=2)
        self.l4 = tk.Label(self.tframe, textvariable=self.blob2, justify='left', font='Helvetica 10')
        self.l4.grid(row=3, columnspan=2)

    
    def update_image(self):    
        # Получаем последний кадр
        self.OGimage = cv2.cvtColor(self.cap.read()[1], cv2.COLOR_BGR2RGB) # to RGB
        self.OGimage = Image.fromarray(self.OGimage) # to PIL format
        self.image = self.OGimage.resize((960, 1080), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        js = requests.get('http://localhost:5000/get_trains').json()
        tracks = js['tracks']
        state = js['state']
        newt = ''
        for i in tracks:
            if tracks[i]:
                newt += i + ' путь: обнаружено ' + str(tracks[i]) + ' объектов\n'
            else:
                newt += i + ' путь: свободен'
        self.blob.set(newt)
        self.blob2.set(state + '\n\n' + js['journal'])
        self.window.after(self.interval, self.update_image)
        print(state)

if __name__ == "__main__":
    root = tk.Tk()
    mw = MainWindow(root, cv2.VideoCapture("rtsp://localhost:8001/stream"))
    root.mainloop()

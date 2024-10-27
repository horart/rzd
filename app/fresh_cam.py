#!/usr/bin/env python3

'''
Получение последнего кадра с камеры
==============================================
Использование:
------
    freshest_camera_frame.py
Клавиши:
-----
    ESC   - выход
'''

from __future__ import print_function

import os
import sys
import time
import threading
import numpy as np
import cv2 as cv

# Запуск класса
class FreshestFrame(threading.Thread):
	def __init__(self, capture, name='FreshestFrame'):
		self.capture = capture
		assert self.capture.isOpened()
		
		self.cond = threading.Condition()

		self.running = False

		self.frame = None

		self.latestnum = 0
		
		self.callback = None
		
		super().__init__(name=name)
		self.start()

	def start(self):
		self.running = True
		super().start()

	def release(self, timeout=None):
		self.running = False
		self.join(timeout=timeout)
		self.capture.release()

	def run(self):
		counter = 0
		while self.running:
			(rv, img) = self.capture.read()
			assert rv
			counter += 1

			with self.cond: # lock the condition for this operation
				self.frame = img if rv else None
				self.latestnum = counter
				self.cond.notify_all()

			if self.callback:
				self.callback(img)

	def read(self, wait=True, seqnumber=None, timeout=None):
		"""
		Без аргументов (wait=True) всегда блокируется на новом кадре
		wait=False возвращает текущий кадр
		seqnumber блокирует до появления указанного кадра (или не блокируется вообще)
		timeout может вернуть предыдущий кадр; (0, None) если кадра ещё нет
		"""

		with self.cond:
			if wait:
				if seqnumber is None:
					seqnumber = self.latestnum+1
				if seqnumber < 1:
					seqnumber = 1
				
				rv = self.cond.wait_for(lambda: self.latestnum >= seqnumber, timeout=timeout)
				if not rv:
					return (self.latestnum, self.frame)

			return (self.latestnum, self.frame)

def main():
	cv.namedWindow("frame")
	cv.namedWindow("realtime")

	cap = cv.VideoCapture(0)
	cap.set(cv.CAP_PROP_FPS, 30)

	fresh = FreshestFrame(cap)

	def callback(img):
		cv.imshow("realtime", img)

	fresh.callback = callback

	# Запуск основного цикла
	# Получение последнего кадра, причём этот кадр больше не может повториться
	cnt = 0
	while True:
		t0 = time.perf_counter()
		cnt,img = fresh.read(seqnumber=cnt+1)
		dt = time.perf_counter() - t0
		if dt > 0.010: # 10 milliseconds
			print("NOTICE: read() took {dt:.3f} secs".format(dt=dt))
		print("processing {cnt}...".format(cnt=cnt), end=" ", flush=True)

		cv.imshow("frame", img)
		key = cv.waitKey(200)
		if key == 27:
			break

		print("done!")

	fresh.release()

	cv.destroyWindow("frame")
	cv.destroyWindow("realtime")


if __name__ == '__main__':
	main()

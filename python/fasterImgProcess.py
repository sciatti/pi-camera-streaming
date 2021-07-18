# import the necessary packages
from threading import Thread
import sys
import cv2
import time
#import imutils
import numpy as np
from collections import deque

# # import the Queue class from Python 3
# if sys.version_info >= (3, 0):
# 	from queue import Queue
# # otherwise, import the Queue class for Python 2.7
# else:
# 	from Queue import Queue

class FileVideoStream:
	def __init__(self, queueSize=1028):
		# initialize the file video stream along with the boolean
		# used to indicate if the thread should be stopped or not
		self.stream = cv2.VideoCapture(0)
		self.stopped = False
		# initialize the queue used to store frames read from
		# the video file
		self.Q = deque()
	def start(self):
		# start a thread to read frames from the file video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
	def update(self):
        # keep looping infinitely
		while True:
			# if the thread indicator variable is set, stop the
			# thread
			if self.stopped:
				return
			# otherwise, ensure the queue has room in it
			if len(self.Q) < 1028:
				# read the next frame from the file
				(grabbed, frame) = self.stream.read()
				# if the `grabbed` boolean is `False`, then we have
				# reached the end of the video file
				if not grabbed:
					self.stop()
					return
				# add the frame to the queue
				self.Q.append(frame)
	def read(self):
		# return next frame in the queue
		return self.Q.get()
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
	def more(self):
		# return True if there are still frames in the queue
		return self.Q.qsize() > 0

stopVal = False
fvs = FileVideoStream().start()
time.sleep(5.0)
fvs.stopped = True

print("Frames Expected: ", 30 * 5, " Frames Captured: ", len(fvs.Q))

quit()

while fvs.more():
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale (while still retaining 3
	# channels)
	frame = fvs.read()
	frame = imutils.resize(frame, width=450)
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	frame = np.dstack([frame, frame, frame])
	# display the size of the queue on the frame
	cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
		(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)	
	# show the frame and update the FPS counter
	cv2.imshow("Frame", frame)
	cv2.waitKey(1)
	fps.update()
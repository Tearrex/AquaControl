import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils, time, numpy, time, threading

class Camera(object):
    thread = None
    lastaccess = 0
    vs = None#PiVideoStream(resolution=(640,480), framerate=30)
    frame = None
    flip = False
    def initialize(self):
        if not Camera.thread:
            Camera.vs = PiVideoStream(resolution=(640,480), framerate=30)
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            while not self.frame: time.sleep(0)
    def __del__(self):
        self.vs.stop()
    @classmethod
    def do_flip(cls, frame):
        if cls.flip: return numpy.flip(frame, 0)
        return frame
    def get_frame(self):
        Camera.lastaccess = time.time()
        self.initialize()
        #frame = self.do_flip(self.vs.read())
        #ret, jpg = cv2.imencode('.jpg', frame)
        return self.frame
    @classmethod
    def _thread(cls):
        cls.vs.start()
        time.sleep(2)
        while True:
            
            fframe = cls.do_flip(cls.vs.read())
            ret, jpg = cv2.imencode('.jpg', fframe)
            cls.frame = jpg.tobytes()

            if time.time() - cls.lastaccess > 5:
                break
        cls.vs.stop()
        cls.thread = None
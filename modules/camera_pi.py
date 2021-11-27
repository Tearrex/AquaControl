import io, time, threading, cv2
try:
    from picamera.array import PiRGBArray
    import picamera
except ImportError: pass
try: from thread import get_ident
except ImportError: from _thread import get_ident

class CameraEvent(object):
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        _id = get_ident()
        if _id not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[_id] = [threading.Event(), time.time()]
        return self.events[_id][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for id, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = id
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()

class Camera(object):
    last_access = 0
    frame = None
    thread = None
    rawCapture = None
    stream = None
    event = CameraEvent()
    enabled = False
    def initialize(self):
        if not Camera.thread:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()
            while not self.frame: time.sleep(0)
    def toggle_stream(self, bool):
        Camera.enabled = bool
    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        Camera.event.wait()
        Camera.event.clear()
        return self.frame
    @classmethod
    def _thread(cls):
        print("Stream requested, initiating thread")
        with picamera.PiCamera() as cam:
            cam.resolution = (640,480)
            cam.framerate = 32
            cam.hflip = False
            cam.vflip = False
            rawCapture = PiRGBArray(cam, size=(640,480))
            cls.stream = cam.capture_continuous(rawCapture, format="bgr", use_video_port=True)
            #cam.start_preview()
            time.sleep(2)
            for f in cls.stream:
                ret, jpg = cv2.imencode('.jpg', f.array)
                cls.frame = jpg.tobytes()
                Camera.event.set()
                rawCapture.truncate(0)
                if time.time() - cls.last_access > 7:
                    rawCapture.close()
                    cls.stream.close()
                    cls.enabled = False
                    cls.frame = None
                    break
        print("Stream inactive, removing thread")
        cls.thread = None
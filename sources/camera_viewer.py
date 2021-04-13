import camera_viewer_ui
import cv2 as cv
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import os
import time
import numpy as np

class CameraViewer(camera_viewer_ui.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(CameraViewer, self).__init__()
        self.setupUi(self)
        list_devices = os.listdir('/dev')
        list_videos = [s for s in list_devices if "video" in s]
        for video in list_videos:
            self.comboBoxCamera.addItem("/dev/"+video)
        
        self.cameraGrabber = CameraGrabber("/dev/cam0")
        self.cameraGrabber.new_image_signal.connect(self.update_image)
        self.pushButtonStart.clicked.connect(self.run_camera)
        self.pushButtonStop.clicked.connect(self.stop_camera)

    def run_camera(self):
        self.cameraGrabber.startGrabber()
        self.cameraGrabber.start()
    
    def stop_camera(self):
        self.cameraGrabber.stopGrabber()

    def closeEvent(self, event):
        if self.cameraGrabber.isRunning():
            self.cameraGrabber.stopGrabber()
            self.cameraGrabber.exit()
            while self.cameraGrabber.isRunning():
                pass
    
    @Slot(np.ndarray)
    def update_image(self, frame):
        h, w, c = frame.shape
        image = QImage(frame.data, w, h, 3*w, QImage.Format_RGB888)
        pixmap = QPixmap(image)
        scene = QGraphicsScene()
        scene.addPixmap(pixmap)
        self.graphicsView.setScene(scene)

class CameraGrabber(QThread, QObject):
    new_image_signal = Signal(np.ndarray)

    def __init__(self, cam_name):
        super(CameraGrabber, self).__init__()
        self._cam_name = cam_name
        self._grabbing = True
    
    def run(self):
        cap = cv.VideoCapture(0)
        while(self._grabbing):
            ret, frame = cap.read()
            if ret:
                frame_small = cv.resize(frame, (640, 480))
                frame_small_rgb = cv.cvtColor(frame_small, cv.COLOR_BGR2RGB)
                self.new_image_signal.emit(frame_small_rgb)
        cap.release()
        
    def startGrabber(self):
        self._grabbing = True

    def stopGrabber(self):
        self._grabbing = False

if __name__ == "__main__":
    cam_viewer = QApplication()
    cam_viewer_gui = CameraViewer()
    cam_viewer_gui.show()
    cam_viewer.exec_()
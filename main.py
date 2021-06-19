## Unrealated to CameraXF, the QR reader dependency libzbar
## can be difficult to build, if the Buildozer build fails with:
##        configure.ac:109: error: possibly undefined macro: AM_ICONV
## then install gettext:
##        sudo apt-get install gettext
##
## if all else fails set this False to exclude the QRReader from the example.
add_qrreader = True

# see BUILDOZER_README.txt for buildozer.spec settings

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from android.permissions import request_permissions, check_permission, \
    Permission
from android import api_version    
from cameraxf import CameraXF
from toast import Toast
if add_qrreader:
    from qrreader import QRReader

class MyApp(App):
    
    def build(self):
        self.cameraxf = None
        self.qrreader = None
        permissions = [Permission.CAMERA, Permission.RECORD_AUDIO]
        if api_version < 29:
            # Use File System not MediaStore
            permissions.append(Permission.WRITE_EXTERNAL_STORAGE)
        request_permissions(permissions)
        l0 = Label(text=
                   'Dismiss a camera with the\nback button or a back gesture')
        b1 = Button(text= 'Tap for Photo Camera', on_press = self.camera_photo)
        b2 = Button(text= 'Tap for Video Camera', on_press = self.camera_video)
        b3 = Button(text= 'Tap for Mirror', on_press = self.camera_mirror)
        b4 = Button(text= 'Tap for QR reader', on_press = self.camera_qrcode)
        box = BoxLayout(orientation='vertical')
        box.add_widget(l0)
        box.add_widget(b1)
        box.add_widget(b2)
        box.add_widget(b3)
        if add_qrreader:
            box.add_widget(b4)
        return box

    def camera_photo(self,b):
        if check_permission(Permission.CAMERA):
            if api_version > 28 or\
               check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                self.cameraxf = CameraXF(capture='photo',
                                         flash='auto',
                                         callback=self.captured)
                self.cameraxf.bind(on_dismiss=self._dismissed)

    def camera_video(self,b):
        if check_permission(Permission.CAMERA) and\
           check_permission(Permission.RECORD_AUDIO):
            if api_version > 28 or\
               check_permission(Permission.WRITE_EXTERNAL_STORAGE):
                self.cameraxf = CameraXF(capture='video',
                                         callback=self.captured)
                self.cameraxf.bind(on_dismiss=self._dismissed)

    def camera_mirror(self,b):
        if check_permission(Permission.CAMERA):
            self.cameraxf = CameraXF(capture='none',
                                     zoom = 0,
                                     facing='front')
            self.cameraxf.bind(on_dismiss=self._dismissed)

    def camera_qrcode(self,b):
        if check_permission(Permission.CAMERA):
            self.cameraxf = CameraXF(capture='data',
                                     callback=self.analyze)
            if add_qrreader:
                self.qrreader = QRReader(self.cameraxf)
            self.cameraxf.bind(on_dismiss=self._dismissed)

    def _dismissed(self,w):
        self.cameraxf = None
        self.qrreader = None

    def captured(self,file_id):
        if not 'ERROR:' in file_id[:6]:
            file_id = 'Saved as:\n' + file_id
        Toast().show(file_id)

    def analyze(self,image_proxy):
        if self.qrreader:
            self.qrreader.analyze(image_proxy)
        
    def on_pause(self):
        if self.cameraxf:
            self.cameraxf.pause()
        return True

    def on_resume(self):
        if self.cameraxf:
            self.cameraxf.resume()

        
MyApp().run()


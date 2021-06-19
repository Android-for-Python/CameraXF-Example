# Android *only* Camera for Kivy, *full screen only*.
# >>>>>> see BUILDOZER_README.txt <<<<<<
#
# Capture photo, video, or data; both cameras; zoom; focus.
#
# An implementation of Android CameraX
# About CameraX:
#    https://developer.android.com/training/camerax
# Available devices:
#    https://developer.android.com/training/camerax/devices
#
# Kivy Base Class: ModalView
# The contents of this ModalView are Android Views, not Kivy Widgets. Inside
# this ModalView Kivy does not paint the screen or get touch events from the
# screen. Painting and touch handling are done using the Android Java API via
# Pyjnius.
#
#
# CameraXF Class initialization parameters:
###########################################
#
#   capture = (string) 'photo', 'video', 'data', 'none'    default 'none'
#   facing = (string) 'back' or 'front',                   default 'back'
#   callback = None                                      see *Callback* below
#
# This applies only when capture = 'photo' , 'video' or 'data':
#   aspect_ratio = (string) '4:3', '16:9' 
#                                   default photo '4:3' , video or data '16:9'
#   Preview image size will be the largest that can be contained
#   within the available pixels on the screen given the aspect ratio.
#
#   Photo and video image size will the largest provided by the
#   chip that also meets the jpg and mp4 conventions and the aspect ratio.
#
#   Data analysis resolution is determined from the aspect ratio, and is
#   documented by CameraX as a maximum of 1080p.
#   The data analysis resolution will degrade gracefully and automatically
#   as determined by the latency introduced by the app's analysis of the data.
#
# This applies only when capture = 'data':
#   resolution = (tuple or list)  eg [640,480]
#
#   This overrides aspect_ratio with a specific maximum screen and data
#   analysis resolution (and hence aspect ratio).
#   Use if the analysis implementation expects a specific resolution; note that
#   the actual resolution will be the the nearest supported by the image chip
#   on the device, and may(?) be subject to the graceful degradation mechanism
#   described above.
#   The order of the parameters is not significant.
#
# These apply only when capture = 'photo' or 'video':
#   private = (boolean) True use Private storage         default Public storage
#   optimize = (string) 'latency', 'quality',              default 'latency'
#   flash = (string) 'on', 'off', 'auto'                   default 'off'
#
# *Callback*
# callback must be a user supplied method with the signature:
#                              def callbackname(self, argument):
# For 'photo' and 'video' the argument is a string containing either
#    a file path, a MediaStore reference, or an error (starts with 'ERROR:')
#    On devices running Android 9 or less, the file path is of the form
#    '/somepath/DCIM/AppName/Date/Time.jpg'.
#    On devices running Android 10 more, the MediaStore reference is of the form
#    'DCIM/AppName/Date/Time.jpg' where 'DCIM/AppName/Date/' is the
#    'RELATIVE_PATH' and 'Time.jpg' is the 'DISPLAY_NAME'. 
# For 'data' the argument is a Java ImageProxy: androidx.camera.core.ImageProxy
#
# Android permissions:
#   CAMERA is required
#   RECORD_AUDIO is only required for 'video'
#   WRITE_EXTERNAL_STORACE is required for storage whan api <=28 and should
#   not be requested when api>= 30
#   These permissions must be requestin in the app and buildozer.spec
#   request_permissions([Permission.CAMERA,Permission.RECORD_AUDIO,
#                        Permission.WRITE_EXTERNAL_STORAGE])
#
# Source https://github.com/RobertFlatt/Android-for-Python/cameraxf
#
# build note: in the example pyzbar may fail to build, try this:
# sudo apt-get update
# sudo apt-get install gettext
# 

from kivy.core.window import Window
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from functools import partial
from android.runnable import run_on_ui_thread
from inspect import ismethod, signature
from cameraxf.camerax import CameraX
from cameraxf.layoutxf import LayoutXF

class CameraXF(ModalView):
    def __init__(self,
                 capture = 'none',
                 facing = 'back',
                 aspect_ratio = 'default',  
                 flash = 'off',
                 optimize = 'latency',
                 resolution = None,
                 private_storage = False,
                 zoom = 0.5,
                 callback = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.camerax = None
        self.layout = None
        self.enable_dismiss = True
        self.disable_annotate = False
        ##############################
        # Option handling
        ##############################
        capture = capture.lower()
        facing = facing.lower()
        aspect_ratio = aspect_ratio.lower()
        flash = flash.lower()
        optimize = optimize.lower()

        self.capture = False
        self.video = False
        self.analysis = False
        if capture == 'photo':
            self.capture = True
        elif capture == 'video':
            self.capture = True
            self.video = True
        elif capture == 'data':
            self.analysis = True

        if aspect_ratio == 'default':
            if capture == 'photo':
                aspect_ratio = '4:3'
            elif capture == 'video':
                aspect_ratio = '16:9'
            elif capture == 'data':
                aspect_ratio = '16:9'
            else:
                aspect_ratio = 'crop'
        elif aspect_ratio not in ['4:3','16:9','crop']:
            aspect_ratio = 'crop'

        if facing not in ['back','front']:
            facing = 'back'

        if flash not in ['on','off','auto']:
            flash = 'off'

        if optimize not in ['latency','quality']:
            optimize = 'latency'

        if resolution and\
           (type(resolution) is tuple or type(resolution) is list) and\
           len(resolution) == 2:
            # camerax will resort these according to current orientation
            resolution = [max(resolution),min(resolution)]
        else:
            resolution = None

        zoom = min(max(zoom,0),1)

        if callback:
            if not ismethod(callback) or\
               len(signature(callback).parameters) !=1:
                callback = None

        ##############################
        # Create Camera
        ##############################
        self.layout = LayoutXF(
            video_toggle = self.video_toggle,
            photo_take = self.photo_take,
            other_camera = self.other_camera,
            touch_action = self._preview_touch_action,
            dismiss = self.dismiss,
            aspect_ratio = aspect_ratio)

        self.camerax = CameraX(
            capture = self.capture,
            video = self.video,
            analysis = self.analysis,
            facing = facing,
            resolution = resolution,
            aspect_ratio = aspect_ratio,
            callback = callback,
            flash = flash,
            optimize = optimize,
            zoom = zoom,
            private = private_storage)   

        ##############################
        # Initialize Camera
        ##############################
        self.open()

    ##############################
    # Lifecycle events
    ##############################
    def on_open(self):
        self.build_layout()

    def on_dismiss(self):
        if self.enable_dismiss:
            self.enable_dismiss = False
            self.disable_annotate = True
            if self.layout:
                self.layout.deactivate_listeners()
            self.video_stop()
            self._unbind_camera()
            if self.layout:
                self.layout.destroy_layout()
            self.camerax = None
            self.layout = None
            Clock.schedule_once(self.begone_you_black_screen)

    def on_size(self, instance, size):
        self.disable_annotate = True
        self.video_stop()
        if self.layout and self.layout.instantiated:
            self.layout.orientation(self.capture, self.video,
                                    self.width,self.height)
            # This fixes the vertical stretch on rotation from
            # initial orientation
            # Seems like a PreviewView issue,
            # but maybe I just don't understand.
            if self.camerax:
                self.camerax.bind_camera(self.layout.imgview)
        self.disable_annotate = False


    def resume(self):
        # Required if the device is rotated between pause and resume
        # perhaps a p4a issue ?
        self.on_size(0,0)

    def pause(self):
        self.video_stop()

    ##############################
    # UI events
    ##############################
    def video_stop(self):
        if self.camerax:
            self.layout.button_red(False,0)
            self.camerax.video_stop()

    def video_start(self):
        if self.camerax:
            self.layout.button_red(True,0)
            self.camerax.video_start()

    def video_toggle(self):
        if self.camerax:
            if self.camerax.video_is_recording:
                self.video_stop()
            else:
                self.video_start()

    def photo_take(self):
        if self.camerax:                     
            self._photo_button_red()
            self.camerax.photo_take()

    def other_camera(self):
        if self.camerax:
            self.camerax.other_camera()

    def _preview_touch_action(self,type,x,y,scale):
        if self.camerax:
            self.camerax.touch_action(type,x,y,scale)

    ##############################
    # Layout
    ##############################
    def build_layout(self):
        if self.layout:
            if self.capture and self.video:
                self.layout.video_layout()
            elif self.capture:
                self.layout.photo_layout()
            elif self.analysis:
                self.layout.analyze_layout()
            else:
                self.layout.none_layout()
            self.layout.orientation(self.capture, self.video,
                                    self.width,self.height)
            self.layout.instantiate(self.camerax.bind_camera,
                                    self.capture, self.video)

    ##############################
    # Utils
    ##############################
    def _photo_button_red(self):
        self.layout.button_red(True,0)
        Clock.schedule_interval(partial(self.layout.button_red,False),0.3)

    @run_on_ui_thread
    def _unbind_camera(self):
        if self.camerax:
            self.camerax.unbind_camera()

    # Sometimes on_dismiss the calling Kivy code has a black screen,
    # but its event loop is running.
    # This workaround is scheduled to occur after on_dismiss.
    def begone_you_black_screen(self,dt):
        Window.update_viewport()            



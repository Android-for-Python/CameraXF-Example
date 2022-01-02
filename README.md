CameraXF
========

**DEPRECATED use [c4k_photo_example](https://github.com/Android-for-Python/c4k_photo_example)**

*A Kivy Android Camera2 implementation*

- CameraXF is a turnkey, full screen, photo, video, data analaysis camera.

- CameraXF depends on the master version of Buildozer installed locally after 2021/04/21 (this adds android.enable_androidx). Update your version with pip3 if necessary.

- CameraXF depends on Android's CameraX api, this is a [device independent](https://developer.android.com/training/camerax/devices) version of Android's Camera2 api.

Building the QR reader, and hence the whole example, depends gettext. Do this first, if your Linux already has gettext installed then this will be a no-op.

	 sudo apt-get install gettext

The repository includes a buildozer.spec, the changes to the default buildozer.spec are documented in [BUILDOZER_README.txt](https://github.com/Android-for-Python/CameraXF-Example/blob/main/README.md)

The example has 4 buttons. On the home screen select a Photo Camera, a Video Camera, a Mirror, or a QR code reader. A back gesture or back button returns you to the buttons.

Try pause/resume, rotation, pinch zoom, tap for focus/exposure, the Photo Camera has a button to switch cameras dynamically. If a video is currently being recorded then, a pause, a back gesture/button, or rotating the camera between portrait and landscape (when .spec orientation = all) will cause the recording to stop and be saved. This is the expected behavior.

Images and videos are saved by default to public storage, organized by date and time. A toast shows the file path or MediaStore reference on which an app could operate. On devices running Android 9 or less, the file path is of the form `/somepath/DCIM/AppName/Date/Time.jpg`. On devices running Android 10 or more, the MediaStore reference is of the form `DCIM/AppName/Date/Time.jpg`. 

The QR reader displays its results on screen; it should be viewed as a simple example of image analysis and image decorating as it does not implement a 'go to' functionality of a typical QR app. 

The camera is full screen ONLY, messing with the layouts is for fools and experts as the layouts are implemented in Java and Android View classes. Details of the [API](https://github.com/Android-for-Python/CameraXF-Example/blob/main/cameraxf/cameraxf.py).

Captain Obvious pointed out that he wants a widget he could embed in a Kivy layout, rather than a full screen widget which is instantiated from a Kivy layout. One step at a time bro.




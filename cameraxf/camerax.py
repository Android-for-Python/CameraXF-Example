import datetime
from android.storage import app_storage_path, primary_external_storage_path
from android.runnable import run_on_ui_thread
from android import api_version
from jnius import autoclass, cast
from os.path import exists, join
from os import mkdir
from cameraxf.listeners import TouchListener, CallbackWrapper

# General
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Environment = autoclass('android.os.Environment')
File = autoclass('java.io.File')
Size = autoclass('android.util.Size')
Context = autoclass('android.content.Context')
if api_version < 28:
    ContextCompat = autoclass('androidx.core.content.ContextCompat')
# MediaStore
MediaStore = autoclass('android.provider.MediaStore')
MediaStoreImagesMedia = autoclass('android.provider.MediaStore$Images$Media')
MediaStoreVideoMedia = autoclass('android.provider.MediaStore$Video$Media')
MediaStoreMediaColumns = autoclass('android.provider.MediaStore$MediaColumns')
ContentValues = autoclass('android.content.ContentValues')

# CameraX components:
PreviewBuilder = autoclass('androidx.camera.core.Preview$Builder')
AspectRatio = autoclass('androidx.camera.core.AspectRatio')
ImageCapture = autoclass('androidx.camera.core.ImageCapture') 
ImageCaptureBuilder = autoclass('androidx.camera.core.ImageCapture$Builder')
ImageCaptureOutputFileOptionsBuilder = autoclass('androidx.camera.core.ImageCapture$OutputFileOptions$Builder')
VideoCaptureBuilder = autoclass('androidx.camera.core.VideoCapture$Builder')
VideoCaptureOutputFileOptionsBuilder = autoclass('androidx.camera.core.VideoCapture$OutputFileOptions$Builder')
FocusMeteringActionBuilder = autoclass('androidx.camera.core.FocusMeteringAction$Builder')
ImageAnalysis = autoclass('androidx.camera.core.ImageAnalysis')
ImageAnalysisBuilder = autoclass('androidx.camera.core.ImageAnalysis$Builder')
ProcessCameraProvider = autoclass('androidx.camera.lifecycle.ProcessCameraProvider')
UseCaseGroupBuilder = autoclass('androidx.camera.core.UseCaseGroup$Builder') 
CameraSelector = autoclass('androidx.camera.core.CameraSelector')
CameraSelectorBuilder = autoclass('androidx.camera.core.CameraSelector$Builder')
ProcessLifecycleOwner = autoclass('androidx.lifecycle.ProcessLifecycleOwner')
CameraInfo =autoclass('androidx.camera.core.CameraInfo')

CameraChars = autoclass('android.hardware.camera2.CameraCharacteristics')
CameraMetadata = autoclass('android.hardware.camera2.CameraMetadata')

# Local Java
ImageSavedCallback = autoclass('org.kivy.camerax.ImageSavedCallback')
VideoSavedCallback = autoclass('org.kivy.camerax.VideoSavedCallback')
ImageAnalysisAnalyzer = autoclass('org.kivy.camerax.ImageAnalysisAnalyzer')
    

class CameraX():
    def __init__(self,
                 capture,
                 video,
                 analysis,
                 facing,
                 resolution,
                 aspect_ratio,
                 callback,
                 flash,
                 optimize,
                 zoom,
                 private,
                 **kwargs):
        super().__init__(**kwargs)

        self.capture = capture
        self.video = video
        self.analysis = analysis
        self.resolution = resolution
        self.callback = callback
        self.private = private
        self.zoom = zoom
        self.name_pipe = []

        self.ASPECT_RATIO_NONE = 432
        if aspect_ratio == '16:9':
            self.aspect_ratio = AspectRatio.RATIO_16_9
        elif aspect_ratio == '4:3':
            self.aspect_ratio = AspectRatio.RATIO_4_3
        elif aspect_ratio == 'crop' and not self.capture:
            self.aspect_ratio = self.ASPECT_RATIO_NONE
        else:
            self.aspect_ratio = AspectRatio.RATIO_4_3
            
        if facing == 'front':
            self.lens_facing = CameraSelector.LENS_FACING_FRONT
        elif facing == 'back':
            self.lens_facing = CameraSelector.LENS_FACING_BACK
        else:
            self.lens_facing = CameraSelector.LENS_FACING_BACK
            
        if optimize == 'quality':
            self.optimize = ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY
        elif optimize == 'latency':
            self.optimize = ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY
        else:
            self.optimize = ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY
            
        if flash == 'on':
            self.flash_mode = ImageCapture.FLASH_MODE_ON
        elif flash == 'auto':
            self.flash_mode = ImageCapture.FLASH_MODE_AUTO
        elif flash == 'off':
            self.flash_mode = ImageCapture.FLASH_MODE_OFF
        else:
            self.flash_mode = ImageCapture.FLASH_MODE_OFF

        self.cameraProvider = None
        self.video_is_recording = False


    ##############################
    # Android CameraX
    ##############################
    def bind_camera(self,preview_view):
        if self.analysis:
            # Java class can't be set on ui thread
            self.ia_wrapper = CallbackWrapper(self.callback)
            self.set_degrees()
            if self.resolution:
                self.rresolution = []
                if self.degrees in [0,180]:
                    # Landscape
                    self.rresolution.append(max(self.resolution))
                    self.rresolution.append(min(self.resolution))
                else:
                    self.rresolution.append(min(self.resolution))
                    self.rresolution.append(max(self.resolution))
        self._bind_camera_ui(preview_view)

    @run_on_ui_thread        
    def _bind_camera_ui(self,preview_view):   
        self.preview_view = preview_view   
        # CameraProvider
        context =  cast('android.content.Context',
                        PythonActivity.mActivity.getApplicationContext())
        try:
            cpf = ProcessCameraProvider.getInstance(context)
        except Exception as e:
            print('ERROR CameraX.bind_camera():\n' + str(e))
            
        self.cameraProvider = cpf.get()
        self.cameraProvider.unbindAll()

        # CameraSelector
        csb = CameraSelectorBuilder()
        csb.requireLensFacing(self.lens_facing)
        cameraSelector = csb.build()

        # ImageAnalysis
        if self.analysis:
            wm =  PythonActivity.mActivity.getWindowManager()
            self.rotation = wm.getDefaultDisplay().getRotation()

            strategy = ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST
            self.ib = ImageAnalysisBuilder()
            if self.resolution:
                self.ib.setTargetResolution(Size(self.rresolution[0],
                                                 self.rresolution[1]))
            else:
                self.ib.setTargetAspectRatio(self.aspect_ratio)
            self.ib.setBackpressureStrategy(strategy)
            self.ib.setTargetRotation(self.rotation)
            self.imageAnalysis = self.ib.build()
            if api_version < 28:
                self.te = ContextCompat.getMainExecutor(context)
            else:
                self.te = context.getMainExecutor()
            self.iaa = ImageAnalysisAnalyzer(self.ia_wrapper)
            self.imageAnalysis.setAnalyzer(self.te, self.iaa)

        # ImageCapture
        if self.capture:
            mActivity =  PythonActivity.mActivity
            rot = mActivity.getWindowManager().getDefaultDisplay().getRotation()
            if self.video:
                self.cb = VideoCaptureBuilder()
            else:
                self.cb = ImageCaptureBuilder()
                self.cb.setFlashMode(self.flash_mode)
                self.cb.setCaptureMode(self.optimize)
            self.cb.setTargetAspectRatio(self.aspect_ratio)
            self.cb.setTargetRotation(rot)
            self.imageCapture = self.cb.build()

        # Preview
        pb = PreviewBuilder()
        if self.analysis and self.resolution:
            pb.setTargetResolution(Size(self.rresolution[0],
                                        self.rresolution[1])) 
        elif self.capture or self.analysis:
            if self.aspect_ratio == AspectRatio.RATIO_4_3 or\
               self.aspect_ratio == AspectRatio.RATIO_16_9:
                pb.setTargetAspectRatio(self.aspect_ratio)
        preview = pb.build()
        preview.setSurfaceProvider(preview_view.getSurfaceProvider())


        # UseCase
        ucgb = UseCaseGroupBuilder()
        ucgb.addUseCase(preview)
        if self.capture:
            ucgb.addUseCase(self.imageCapture)
        if self.analysis:
            ucgb.addUseCase(self.imageAnalysis)
        #if previewview:
        ucgb.setViewPort(preview_view.getViewPort())  
        useCaseGroup = ucgb.build()
        
        # Bind
        self.cam = self.cameraProvider.bindToLifecycle(ProcessLifecycleOwner.get(),
                                                       cameraSelector,
                                                       useCaseGroup)
        self.cam.cameraControl.setLinearZoom(self.zoom)
        self.focus(0.5,0.5)

    @run_on_ui_thread        
    def unbind_camera(self):
        if self.cameraProvider:
            self.cameraProvider.unbindAll()

        
    ##############################
    # User Events
    ##############################
    def other_camera(self):
        if self.lens_facing == CameraSelector.LENS_FACING_FRONT:
            self.lens_facing = CameraSelector.LENS_FACING_BACK
        else:
            self.lens_facing = CameraSelector.LENS_FACING_FRONT
        self.bind_camera(self.preview_view)
    
    def focus(self,x,y):
        factory = self.preview_view.getMeteringPointFactory()
        self.point = factory.createPoint(x,y)
        self.action = FocusMeteringActionBuilder(self.point).build()
        if self.cam:
            self.cam.cameraControl.startFocusAndMetering(self.action)
        
    def touch_action(self,type,x,y,scale):
        if type == 'tapup':
            self.focus(x,y)
        elif type == 'scale':
            if self.cam:
                self.zs = self.cam.cameraInfo.getZoomState().getValue()
                scale = self.zs.getZoomRatio() * scale
                scale = min(scale,self.zs.getMaxZoomRatio())
                scale = max(scale,self.zs.getMinZoomRatio())
                self.cam.cameraControl.setZoomRatio(scale)
                self.zs = self.cam.cameraInfo.getZoomState().getValue()
                self.zoom = self.zs.getLinearZoom()

    def video_stop(self):
        if self.video_is_recording:
            self.preview_view.performClick()
            self.imageCapture.stopRecording()
            self.video_is_recording = not self.video_is_recording
        
    def video_start(self):
        if not self.video_is_recording:
            self.preview_view.performClick()
            context = PythonActivity.mActivity.getApplicationContext()
            dt = datetime.datetime.now()
            today = dt.strftime("%Y_%m_%d")
            name = dt.strftime("%H_%M_%S") + '.mp4'
            if self.private or api_version < 29:
                if self.private:
                    root = app_storage_path()
                else:
                    root = primary_external_storage_path()
                    if not root:
                        self.callback("ERROR: No external storage")
                        return
                dir = join(root, Environment.DIRECTORY_DCIM)
                if not exists(dir):
                    mkdir(dir)
                if not self.private:
                    dir = join(dir,self.app_name())
                    if not exists(dir):
                        mkdir(dir)
                dir = join(dir,today)
                if not exists(dir):
                    mkdir(dir)
                self.filepath = join(dir,name)
                self.name_pipe.append(self.filepath)
                self.videofile = File(self.filepath)
                self.vcf = VideoCaptureOutputFileOptionsBuilder(self.videofile).build()
            else:
                self.cr =  PythonActivity.mActivity.getContentResolver()
                collection = MediaStoreVideoMedia.EXTERNAL_CONTENT_URI
                self.cv = ContentValues()
                self.cv.put(MediaStoreMediaColumns.DISPLAY_NAME, name)
                self.cv.put(MediaStoreMediaColumns.MIME_TYPE, "video/mp4")
                self.cv.put(MediaStoreMediaColumns.RELATIVE_PATH,
                            join(Environment.DIRECTORY_DCIM, self.app_name(),today))
                self.vcf = VideoCaptureOutputFileOptionsBuilder(self.cr,
                                                                collection,
                                                                self.cv).build()
            if api_version < 28:
                self.te = ContextCompat.getMainExecutor(context)
            else:
                self.te = context.getMainExecutor()
            self.wrapper = CallbackWrapper(self.callback_wrapper)  
            self.vsc = VideoSavedCallback(self.wrapper)
            self.imageCapture.startRecording(self.vcf,self.te,self.vsc)
            self.video_is_recording = not self.video_is_recording

    def photo_take(self):
        self.preview_view.performClick()
        context = PythonActivity.mActivity.getApplicationContext()
        dt = datetime.datetime.now()
        today = dt.strftime("%Y_%m_%d")
        name = dt.strftime("%H_%M_%S") + '.jpg'

        if self.private or api_version < 29:
            if self.private:
                root = app_storage_path()
            else:
                root = primary_external_storage_path()
                if not root:
                    self.callback("ERROR: No external storage")
                    return
            dir = join(root, Environment.DIRECTORY_DCIM)
            if not exists(dir):
                mkdir(dir)
            if not self.private:
                dir = join(dir,self.app_name())
                if not exists(dir):
                    mkdir(dir)
            dir = join(dir,today)
            if not exists(dir):
                mkdir(dir)
            self.filepath = join(dir,name)
            self.name_pipe.append(self.filepath)
            self.picfile = File(self.filepath)
            self.icf = ImageCaptureOutputFileOptionsBuilder(self.picfile).build()
        else:
            self.cr =  PythonActivity.mActivity.getContentResolver()
            collection = MediaStoreImagesMedia.EXTERNAL_CONTENT_URI
            self.cv = ContentValues()
            self.cv.put(MediaStoreMediaColumns.DISPLAY_NAME, name)
            self.cv.put(MediaStoreMediaColumns.MIME_TYPE, "image/jpeg")
            self.cv.put(MediaStoreMediaColumns.RELATIVE_PATH,
                        join(Environment.DIRECTORY_DCIM, self.app_name(),today))
            self.icf = ImageCaptureOutputFileOptionsBuilder(self.cr,
                                                            collection,
                                                            self.cv).build()
        if api_version < 28:
            self.te = ContextCompat.getMainExecutor(context)
        else:
            self.te = context.getMainExecutor()
        self.wrapper = CallbackWrapper(self.callback_wrapper)  
        self.isc = ImageSavedCallback(self.wrapper)
        self.imageCapture.takePicture(self.icf,self.te,self.isc)

    def callback_wrapper(self, file_id):
        if not file_id:
            # The callback returns "" for non-MediaStore saves
            if self.name_pipe:
                file_id = self.name_pipe[0]
                self.name_pipe = self.name_pipe[1:]
            else:
                return # something is wrong
        self.callback(file_id)

    def app_name(self):
        context = PythonActivity.mActivity.getApplicationContext()
        appinfo = context.getApplicationInfo()
        if appinfo.labelRes:
            name = context.getString(appinfo.labelRes)
        else:
            name = appinfo.nonLocalizedLabel.toString()
        return name


    ##############################
    # Orientation
    ##############################
    # Based on
    # https://developers.google.com/ml-kit/vision/face-detection/android#using-a-media.image
    # Seems overly complex, but I assume it must be that way.

    def set_degrees(self):
        # rotation compensation for analyzer
        wm =  PythonActivity.mActivity.getWindowManager()
        rotation = wm.getDefaultDisplay().getRotation()
        is_front = self.lens_facing == CameraSelector.LENS_FACING_FRONT
        cm = PythonActivity.mActivity.getSystemService(Context.CAMERA_SERVICE)
        rotationCompensation = rotation *90
        cameraId = self.cameraIdForLensFacing(cm, is_front)
        chars = cm.getCameraCharacteristics(cameraId)
        sensorOrientation = chars.get(CameraChars.SENSOR_ORIENTATION)
        if is_front:
            degrees = (sensorOrientation + rotationCompensation) % 360
        else:
            degrees = (sensorOrientation - rotationCompensation + 360) % 360
        self.degrees = degrees

    def cameraIdForLensFacing(self, cameraManager, isFrontFacing):
        # Convert to CameraX enum using Camera2 CameraMetadata
        if isFrontFacing:
            lensFacingInteger = CameraMetadata.LENS_FACING_FRONT
        else:
            lensFacingInteger = CameraMetadata.LENS_FACING_BACK
        for cameraId in cameraManager.getCameraIdList():
            characteristics = cameraManager.getCameraCharacteristics(cameraId)
            cameraLensFacing = characteristics.get(CameraChars.LENS_FACING)
            if cameraLensFacing == int(lensFacingInteger):
                return cameraId
        return '0'    

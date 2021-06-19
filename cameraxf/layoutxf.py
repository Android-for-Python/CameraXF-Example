from android.runnable import run_on_ui_thread
from jnius import autoclass, cast
from os.path import exists
from cameraxf.listeners import TouchListener, ClickListener, KeyListener

# General
PythonActivity = autoclass('org.kivy.android.PythonActivity')
BitmapFactory = autoclass('android.graphics.BitmapFactory')
Bitmap = autoclass('android.graphics.Bitmap')
PorterDuffMode = autoclass('android.graphics.PorterDuff$Mode')

# View Layout:
View = autoclass('android.view.View')
ViewGroup = autoclass('android.view.ViewGroup')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
LLayoutParams = autoclass('android.widget.LinearLayout$LayoutParams')
LinearLayout = autoclass('android.widget.LinearLayout')
RelativeLayout = autoclass('android.widget.RelativeLayout')
FrameLayout = autoclass('android.widget.FrameLayout')
KeyEvent = autoclass('android.view.KeyEvent')
ImageButton = autoclass('android.widget.ImageButton')
Gravity = autoclass('android.view.Gravity')
PreviewView = autoclass('androidx.camera.view.PreviewView')
ScaleType = autoclass('androidx.camera.view.PreviewView$ScaleType')
SurfaceView = autoclass('android.view.SurfaceView')
PixelFormat = autoclass('android.graphics.PixelFormat')

class LayoutXF():
    def __init__(self,
                 video_toggle,
                 photo_take,
                 other_camera,
                 touch_action,
                 dismiss,
                 aspect_ratio,
                 **kwargs):    
        super().__init__(**kwargs)
        self.video_toggle = video_toggle
        self.photo_take = photo_take
        self.other_camera = other_camera
        self.touch_action = touch_action
        self.dismiss = dismiss
        self.aspect_ratio = aspect_ratio
        self.layout = None
        self.capturebutton = None
        self.flipbutton = None
        self.imgview = None
        self.instantiated = False
        self.touch_listener = None
        self.key_listener = None
        self.flip_listener = None
        self.click_listener = None
        self.visibility = None
    
    ##############################
    # Layout
    # Icons downloaded from https://material.io/resources/icons
    ##############################
    def scale_bitmap(self, bitmap):
        context = PythonActivity.mActivity.getApplicationContext()
        density = context.getResources().getDisplayMetrics().density
        self.edge = round(density * 256 / 3)
        return Bitmap.createScaledBitmap(bitmap, self.edge, self.edge, True)

    @run_on_ui_thread        
    def video_layout(self):
        context =   PythonActivity.mActivity.getApplicationContext()
        self.imgview = PreviewView(context)
        self.imgview.setLayoutParams(LayoutParams(-1,-1))  
        self.imgview.setScaleType(ScaleType.FIT_CENTER)
        icon = 'cameraxf/icons/videocam_white.png'
        self.capturebutton = ImageButton(context)
        if exists(icon):
            bitmap = BitmapFactory.decodeFile(icon)
            bitmap = self.scale_bitmap(bitmap)
            self.capturebutton.setLayoutParams(LayoutParams(self.edge,
                                                            self.edge))
            self.capturebutton.setImageBitmap(bitmap)

        self.buttonslayout = LinearLayout(context)
        self.buttonslayout.setGravity(Gravity.CENTER)
        self.buttonslayout.setBackgroundColor(-16777216) #Black
        self.buttonslayout.addView(self.capturebutton)

        self.imagelayout = LinearLayout(context)
        self.imagelayout.setBackgroundColor(-16777216) #Black
        self.imagelayout.setGravity(Gravity.CENTER)
        self.imagelayout.addView(self.imgview)
 
        self.layout = LinearLayout(context)
        self.layout.setLayoutParams(LLayoutParams(-1,-1))
        self.layout.addView(self.imagelayout)
        self.layout.addView(self.buttonslayout)
        
    @run_on_ui_thread        
    def photo_layout(self):
        context =   PythonActivity.mActivity.getApplicationContext()
        self.imgview = PreviewView(context)
        self.imgview.setLayoutParams(LayoutParams(-1,-1))  
        self.imgview.setScaleType(ScaleType.FIT_CENTER)
        
        icon = 'cameraxf/icons/photo_camera_white.png'
        self.capturebutton = ImageButton(context)
        if exists(icon):
            bitmap = BitmapFactory.decodeFile(icon)
            bitmap = self.scale_bitmap(bitmap)
            self.capturebutton.setLayoutParams(LayoutParams(self.edge,
                                                            self.edge))
            self.capturebutton.setImageBitmap(bitmap)
        self.flipbutton = ImageButton(context)
        icon = 'cameraxf/icons/flip_camera_white.png'
        if exists(icon):
            bitmap = BitmapFactory.decodeFile(icon)
            bitmap = self.scale_bitmap(bitmap)
            self.flipbutton.setLayoutParams(LayoutParams(self.edge,self.edge))
            self.flipbutton.setImageBitmap(bitmap)

        self.buttonlayout1 = LinearLayout(context)
        self.buttonlayout1.setGravity(Gravity.CENTER)
        self.buttonlayout1.setBackgroundColor(-16777216) #Black
        self.buttonlayout1.addView(self.flipbutton)

        self.buttonlayout0 = LinearLayout(context)
        self.buttonlayout0.setGravity(Gravity.CENTER)
        self.buttonlayout0.setBackgroundColor(-16777216) #Black
        self.buttonlayout0.addView(self.capturebutton)

        self.buttonslayout = LinearLayout(context)
        self.buttonslayout.addView(self.buttonlayout1)
        self.buttonslayout.addView(self.buttonlayout0)

        self.imagelayout = LinearLayout(context)
        self.imagelayout.setBackgroundColor(-16777216) #Black
        self.imagelayout.setGravity(Gravity.CENTER)
        self.imagelayout.addView(self.imgview)
 
        self.layout = LinearLayout(context)
        self.layout.setLayoutParams(LLayoutParams(-1,-1))
        self.layout.addView(self.imagelayout)
        self.layout.addView(self.buttonslayout)

    @run_on_ui_thread        
    def analyze_layout(self):
        context =   PythonActivity.mActivity.getApplicationContext()
        self.capturebutton = None
        self.flipbutton = None
        self.overlay = SurfaceView(context)
        self.overlay.setLayoutParams(LayoutParams(-1,-1))
        self.imgview = PreviewView(context)
        self.imgview.setLayoutParams(LayoutParams(-1,-1)) 
        self.imgview.setScaleType(ScaleType.FIT_CENTER)
        self.layout = FrameLayout(context)
        self.layout.setLayoutParams(LayoutParams(-1,-1)) 
        self.layout.addView(self.overlay)
        self.layout.addView(self.imgview)
        self.overlay.setZOrderOnTop(True)
        self.holder = self.overlay.getHolder()
        self.holder.setFormat(PixelFormat.TRANSLUCENT)

    @run_on_ui_thread        
    def none_layout(self):
        context =   PythonActivity.mActivity.getApplicationContext()
        self.capturebutton = None
        self.flipbutton = None
        self.imgview = PreviewView(context)
        self.imgview.setLayoutParams(LayoutParams(-1,-1))
        self.imgview.setScaleType(ScaleType.FILL_CENTER)
        self.layout = FrameLayout(context)
        self.layout.setLayoutParams(LayoutParams(-1,-1))
        self.layout.addView(self.imgview)

    @run_on_ui_thread   
    def orientation(self,capture,video,width,height):
        if width > height:
            # Remove status bar in Landscape mode
            option = View.SYSTEM_UI_FLAG_FULLSCREEN
        else:
            option = View.SYSTEM_UI_FLAG_VISIBLE
        window = PythonActivity.mActivity.getWindow()
        window.getDecorView().setSystemUiVisibility(option)

        if capture:
            # TODO aspect is discrete depending on image encoding format.
            if self.aspect_ratio == '16:9':
                aspect = 16/9
            else:
                aspect = 4/3
            used = round(min(width,height) * aspect)
            available = max(width,height) - used  # could be -ve!
            buttspace = min(max(available,self.edge),
                            self.edge+round(self.edge/2))
            viewspace = max(width,height) - buttspace
            halfbutton = round(min(width,height) /2)
            self.buttonslayout.setOrientation(width>height)    
            self.layout.setOrientation(height>width)    
        
            if width > height:
                if not video:
                    self.buttonlayout1.setLayoutParams(
                        LLayoutParams(-1,halfbutton))
                    self.buttonlayout0.setLayoutParams(
                        LLayoutParams(-1,halfbutton))
                self.buttonslayout.setLayoutParams(LLayoutParams(buttspace,-1))
                self.imagelayout.setLayoutParams(LLayoutParams(viewspace,-1))
            else:
                if not video:
                    self.buttonlayout1.setLayoutParams(
                        LLayoutParams(halfbutton,-1))
                    self.buttonlayout0.setLayoutParams(
                        LLayoutParams(halfbutton,-1))
                self.buttonslayout.setLayoutParams(LLayoutParams(-1,buttspace))
                self.imagelayout.setLayoutParams(LLayoutParams(-1,viewspace))

    @run_on_ui_thread
    def button_red(self,red,dt):
        if red:
            self.capturebutton.setColorFilter(-65536,PorterDuffMode.MULTIPLY) 
        elif self.capturebutton: # not distroyed during time delay
            self.capturebutton.setColorFilter(None)            
    
    @run_on_ui_thread        
    def instantiate(self, bind_camera, capture, video):
        mActivity = PythonActivity.mActivity 
        mActivity.addContentView(self.layout, LayoutParams(-1,-1))
        self.key_listener = KeyListener(self.dismiss)
        self.touch_listener = TouchListener(self.touch_action)
        self.imgview.setOnKeyListener(self.key_listener)
        self.imgview.setOnTouchListener(self.touch_listener)
        if capture:
            if self.capturebutton:
                if video:
                    self.click_listener = ClickListener(self.video_toggle)
                else:
                    self.click_listener = ClickListener(self.photo_take)
                self.capturebutton.setOnClickListener(self.click_listener)
            if self.flipbutton:
                self.flip_listener = ClickListener(self.other_camera)
                self.flipbutton.setOnClickListener(self.flip_listener)
        self.instantiated = True
        bind_camera(self.imgview)


    @run_on_ui_thread        
    def destroy_layout(self):
        if self.layout:
            parent = cast(ViewGroup, self.layout.getParent())
            if parent is not None: parent.removeView(self.layout)

    def deactivate_listeners(self):
        if self.key_listener:
            self.key_listener.active = False
        if self.touch_listener:
            self.touch_listener.active = False
        if self.click_listener:
            self.click_listener.active = False
        if self.flip_listener:
            self.flip_listener.active = False

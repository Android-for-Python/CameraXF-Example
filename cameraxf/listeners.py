from jnius import PythonJavaClass, java_method, autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
GestureDetector = autoclass('android.view.GestureDetector')
ScaleGestureDetector = autoclass('android.view.ScaleGestureDetector')

class ScaleListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/ScaleGestureDetector$OnScaleGestureListener']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/view/ScaleGestureDetector;)Z')
    def onScaleBegin(self,detector):
        return True

    @java_method('(Landroid/view/ScaleGestureDetector;)Z')
    def onScale(self,detector):
        if self.callback:
            self.callback('scale',0,0, detector.getScaleFactor())
        return True

    @java_method('(Landroid/view/ScaleGestureDetector;)V')
    def onScaleEnd(self,detector):
        pass

class GestureListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/GestureDetector$OnGestureListener']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroid/view/MotionEvent;)Z')
    def onDown(self,e):
        return False

    @java_method('(Landroid/view/MotionEvent;)V')
    def onShowPress(self,e):
        pass

    @java_method('(Landroid/view/MotionEvent;)Z')
    def onSingleTapUp(self,e):
        if self.callback:
            self.callback('tapup',e.getX(),e.getY(),0)
        return True

    @java_method('(Landroid/view/MotionEvent;Landroid/view/MotionEvent;FF)Z')
    def onScroll(self,e1, e2, distanceX, distanceY):
        return False

    @java_method('(Landroid/view/MotionEvent;)V')
    def onLongPress(self,e):
        pass

    @java_method('(Landroid/view/MotionEvent;Landroid/view/MotionEvent;FF)Z')
    def onFling(self, e1, e2, velocityX, velocityY):
        return False


class TouchListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnTouchListener']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.active = True

        self.context =  PythonActivity.mActivity.getApplicationContext()
        self.gesture_listener = GestureListener(self.callback)
        self.gesture_detector = GestureDetector(self.context,
                                                self.gesture_listener)
        self.scale_listener = ScaleListener(self.callback)
        self.scale_detector = ScaleGestureDetector(self.context,
                                                   self.scale_listener)

 
    @java_method('(Landroid/view/View;Landroid/view/MotionEvent;)Z')
    def onTouch(self, v, event):
        if self.active:
            if self.gesture_detector.onTouchEvent(event):
                return True
            if self.scale_detector.onTouchEvent(event):
                return True 
        return False

class ClickListener(PythonJavaClass):
    __javainterfaces__ = ['android.view.View$OnClickListener']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.active = True

    @java_method('(Landroid/view/View;)V')
    def onClick(self, view):
        if self.active:
            self.callback()

class KeyListener(PythonJavaClass):
    __javainterfaces__ = ['android/view/View$OnKeyListener']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.active = True

    @java_method('(Landroid/view/View;ILandroid/view/KeyEvent;)Z')
    def onKey(self, v, key_code, event):
        if event.getAction() == KeyEvent.ACTION_DOWN and\
           key_code == KeyEvent.KEYCODE_BACK: 
            if self.active:
               self.callback()
            return True
        return False

class CallbackWrapper(PythonJavaClass):
    __javacontext__ = 'app'
    __javainterfaces__ = ['org/kivy/camerax/CallbackWrapper']

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    @java_method('(Landroidx/camera/core/ImageProxy;)V')        
    def callback_image(self, image):
        if self.callback:
            self.callback(image)
        
    @java_method('(Ljava/lang/String;)V')        
    def callback_string(self, filepath):
        if self.callback:
            self.callback(filepath)

            

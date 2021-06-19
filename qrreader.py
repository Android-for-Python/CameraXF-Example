from pyzbar import pyzbar
from jnius import autoclass
from PIL import Image
from toast import Toast
from threading import Thread, Event

YuvOperations = autoclass('org.kivy.camerax.YuvOperations')
Paint = autoclass('android.graphics.Paint')
PaintStyle = autoclass('android.graphics.Paint$Style')
Color  = autoclass('android.graphics.Color')
PorterDuffMode = autoclass('android.graphics.PorterDuff$Mode')

# On converting YUV_420_888
# https://blog.minhazav.dev/how-to-convert-yuv-420-sp-android.media.Image-to-Bitmap-or-jpeg/

class QRReader():

    def __init__(self, cameraxf):
        super().__init__()
        self.cameraxf = cameraxf
        self.yuv_operations = YuvOperations()
        self.paintlines = Paint()
        self.paintlines.setStyle(PaintStyle.STROKE)
        self.paintlines.setARGB(255, 255, 0, 0)
        self.paintlines.setStrokeWidth(6)
        self.painttext = Paint()
        self.painttext.setStyle(PaintStyle.FILL_AND_STROKE)
        self.painttext.setARGB(255, 255, 0, 0)
        self.painttext.setStrokeWidth(1)
        self.painttext.setTextSize(50)
        self.busy = False
        self.finished = False
        self.image_available = Event()
        Thread(target=self.manager).start()
        
    def __del__(self):        
        self.finished = True
        self.image_available.set()

    def analyze(self, image_proxy):
        if not self.busy:
            self.busy = True
            self.Y = self.yuv_operations.ImageProxyToYBytesArray(image_proxy)
            self.im_size=(image_proxy.getWidth(),image_proxy.getHeight())
            self.image_available.set()
        image_proxy.close();

    def manager(self):
        while True:
            self.image_available.wait()
            self.image_available.clear()
            if self.finished:
                break
            self.worker()

    def worker(self):
        # This cast takes about 40ms, is there a better way?
        Y = bytes(self.Y)
        pil_image = Image.frombytes(mode='L',size=self.im_size,data=Y)

        #Image.frombuffer("RGBX",len(imgData)+len(info),imgData+info)
        #pil_image = Image.frombytes(mode="YCbCr",size=(w,h),data=Yuv)
        degrees = self.cameraxf.camerax.degrees
        if degrees in [90, 270]:
            degrees = 360 - degrees
        ## 2ms
        pil_image = pil_image.rotate(degrees, expand=1, resample=Image.BICUBIC)
        im_width , im_height = pil_image.size
        if degrees in [0,180]: 
            # Landscape fit height
            scale = self.cameraxf.height / im_height
        else:
            # Portrait fit width
            scale = self.cameraxf.width / im_width        

        # A decode takes about 80mS
        barcodes = pyzbar.decode(pil_image) #,w,h)

        found = []
        for barcode in barcodes:
            x, y, w, h = barcode.rect
            text = barcode.data.decode('utf-8')
            offx = round((self.cameraxf.width - scale * im_width)/2)
            offy = round((self.cameraxf.height - scale * im_height)/2)
            # In screen coordinates:
            left = round(x * scale) + offx
            top  = round(y * scale) + offy
            right = left + round(w * scale)  
            bottom = top + round(h * scale)
            textlen = self.painttext.measureText(text)
            textloc = left + round((right - left - textlen)/2)
            found.append([left,top,right,bottom,text,textloc])

        # Be quiet if rotating
        if self.cameraxf.disable_annotate:
            found = []

        # Write to screen
        # These operations are on a "android.view.SurfaceView"
        if self.cameraxf.layout and self.cameraxf.layout.holder:
            holder = self.cameraxf.layout.holder
            canvas = holder.lockCanvas()
            if canvas:
                canvas.drawColor(0, PorterDuffMode.CLEAR)   
                for f in found:
                    canvas.drawRect(f[0], f[1], f[2], f[3], self.paintlines)
                    canvas.drawText(f[4], f[5], f[1] - 20, self.painttext);
                holder.unlockCanvasAndPost(canvas)
        self.busy = False


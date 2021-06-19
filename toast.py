from android.runnable import run_on_ui_thread
from jnius import autoclass
PythonActivity = autoclass('org.kivy.android.PythonActivity')
JToast = autoclass('android.widget.Toast')
JString = autoclass('java.lang.String')

class Toast():
    
    @run_on_ui_thread         
    def show(self, msg):
        context =   PythonActivity.mActivity.getApplicationContext()
        JToast.makeText(context, JString(msg),JToast.LENGTH_LONG).show()




package org.kivy.camerax;

import androidx.camera.core.ImageProxy;

public interface CallbackWrapper {
    public void callback_image(ImageProxy image);
    public void callback_string(String filepath);
}


package org.kivy.camerax;

import androidx.camera.core.ImageProxy;
import android.graphics.ImageFormat;
import java.lang.IllegalArgumentException;
import java.nio.ByteBuffer;

public class YuvOperations {

    private byte[] nv21;
    private byte[] Y;

    public YuvOperations() {
	this.nv21 = new byte[0];
	this.Y = new byte[0];
    }

    public byte[] ImageProxyToYuvBytesArray(ImageProxy image) {
	if (image.getFormat() != ImageFormat.YUV_420_888) {
	    throw new IllegalArgumentException("Invalid image format");
	}

	ByteBuffer yBuffer = image.getPlanes()[0].getBuffer();
	ByteBuffer uBuffer = image.getPlanes()[1].getBuffer();
	ByteBuffer vBuffer = image.getPlanes()[2].getBuffer();

	int ySize = yBuffer.remaining();
	int uSize = uBuffer.remaining();
	int vSize = vBuffer.remaining();

	if (this.nv21.length != ySize + uSize + vSize) {
	    this.nv21 = new byte[ySize + uSize + vSize];
	}

	// U and V are swapped
	yBuffer.get(this.nv21, 0, ySize);
	vBuffer.get(this.nv21, ySize, vSize);
	uBuffer.get(this.nv21, ySize + vSize, uSize);

	return this.nv21;
    }

    public byte[] ImageProxyToRGBgrayscaleBytesArray(ImageProxy image) {
	if (image.getFormat() != ImageFormat.YUV_420_888) {
	    throw new IllegalArgumentException("Invalid image format");
	}

	ByteBuffer yBuffer = image.getPlanes()[0].getBuffer();

	int ySize = yBuffer.remaining();

	if (this.nv21.length != ySize * 3) {
	    this.nv21 = new byte[ySize * 3];
	}

	yBuffer.get(this.nv21, 0, ySize);
	yBuffer.get(this.nv21, ySize, ySize);
	yBuffer.get(this.nv21, ySize + ySize, ySize);

	return this.nv21;
    }

    public byte[] ImageProxyToYBytesArray(ImageProxy image) {
	if (image.getFormat() != ImageFormat.YUV_420_888) {
	    throw new IllegalArgumentException("Invalid image format");
	}

	ByteBuffer yBuffer = image.getPlanes()[0].getBuffer();
	int ySize = yBuffer.remaining();

	if (this.Y.length != ySize) {
	    this.Y = new byte[ySize];
	}

	yBuffer.get(this.Y, 0, ySize);

	return this.Y;
    }

}


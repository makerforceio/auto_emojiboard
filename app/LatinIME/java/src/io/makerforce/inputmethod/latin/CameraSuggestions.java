package io.makerforce.inputmethod.latin;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.ImageFormat;
import android.graphics.SurfaceTexture;
import android.hardware.Camera;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.TotalCaptureResult;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.inputmethodservice.InputMethodService;
import android.media.Image;
import android.media.ImageReader;
import android.os.Handler;
import android.os.HandlerThread;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.text.TextUtils;
import android.util.Log;
import android.util.Size;
import android.util.SparseIntArray;
import android.view.Surface;
import android.widget.FrameLayout;
import android.widget.Toast;

import com.vdurmont.emoji.EmojiParser;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.HttpURLConnection;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.net.URL;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static android.support.v4.app.ActivityCompat.shouldShowRequestPermissionRationale;
import static io.makerforce.inputmethod.latin.permissions.PermissionsUtil.requestPermissions;
import static java.security.AccessController.getContext;

/**
 * Created by ambrose on 27/1/18.
 */

public class CameraSuggestions {

    private static final Map<String, String> emojis;
    static {
        emojis = new HashMap<>();
        emojis.put("angry", EmojiParser.parseToUnicode(":angry:,:rage:,:face_with_symbols_over_mouth:,:triumph:"));
//        emojis.put("contempt", "\uF09F\u988C");
//        emojis.put("disgust", "\uF09F\u9896");
        emojis.put("fear", EmojiParser.parseToUnicode(":cold_sweat:,:fearful:,:scream:,:flushed:"));
        emojis.put("happy", EmojiParser.parseToUnicode(":smile:,:joy:,:laughing:,:grin:,:slight_smile:"));
        emojis.put("neutral", EmojiParser.parseToUnicode(":upside_down:,:confused:,:smirk:,:neutral_face:,:expressionless:"));
        emojis.put("sad", EmojiParser.parseToUnicode(":pensive:,:confused:,:unamused:,:worried:,:confounded:,:perservere:"));
        emojis.put("surprise", EmojiParser.parseToUnicode(":astonished:,:open_mouth:,:hushed:,:scream:,:flushed:"));
    }

    private final ArrayList<SuggestedWords.SuggestedWordInfo> suggestions;
    public SuggestedWords suggestedWords = null;

    private ServerSocket mServerSocket;

    private static final SparseIntArray ORIENTATIONS = new SparseIntArray();
    static {
        ORIENTATIONS.append(Surface.ROTATION_0, 90);
        ORIENTATIONS.append(Surface.ROTATION_90, 0);
        ORIENTATIONS.append(Surface.ROTATION_180, 270);
        ORIENTATIONS.append(Surface.ROTATION_270, 180);
    }
    private String cameraId;
    protected CameraDevice cameraDevice;
    protected CameraCaptureSession cameraCaptureSessions;
    protected CaptureRequest captureRequest;
    protected CaptureRequest.Builder captureRequestBuilder;
    private Size imageDimension;
    private static final int REQUEST_CAMERA_PERMISSION = 1;
    private Handler mBackgroundHandler;
    private HandlerThread mBackgroundThread;
    private boolean isEnabled = true;

    private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
        @Override
        public void onOpened(CameraDevice camera) {
            cameraDevice = camera;
            new Thread(new Runnable() {
                @Override
                public void run() {
                    takePictureLoop();
                }
            }).start();
        }
        @Override
        public void onDisconnected(CameraDevice camera) {
            cameraDevice.close();
            isEnabled = false;
        }
        @Override
        public void onError(CameraDevice camera, int error) {
            if (cameraDevice != null) {
                cameraDevice.close();
            }
            cameraDevice = null;
            isEnabled = false;
        }
    };
    private InputMethodService activity;

    protected void startBackgroundThread() {
        mBackgroundThread = new HandlerThread("Camera Background");
        mBackgroundThread.start();
        mBackgroundHandler = new Handler(mBackgroundThread.getLooper());
    }
    protected void stopBackgroundThread() {
        mBackgroundThread.quitSafely();
        try {
            mBackgroundThread.join();
            mBackgroundThread = null;
            mBackgroundHandler = null;
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
    @SuppressLint("MissingPermission")
    private void openCamera() {
        CameraManager manager = (CameraManager) activity.getSystemService(Context.CAMERA_SERVICE);
        Log.e("AUTO", "is camera open");
        try {
            cameraId = manager.getCameraIdList()[1];
            manager.openCamera(cameraId, stateCallback, null);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
        Log.e("AUTO", "openCamera X");
    }
    protected void takePictureLoop() {
        if (null == cameraDevice) {
            Log.e("AUTO", "cameraDevice is null");
            return;
        }
        CameraManager manager = (CameraManager) activity.getSystemService(Context.CAMERA_SERVICE);
        try {
            CameraCharacteristics characteristics = manager.getCameraCharacteristics(cameraDevice.getId());
            int width = 640;
            int height = 480;
            ImageReader reader = ImageReader.newInstance(width, height, ImageFormat.JPEG, 1);
            final CaptureRequest.Builder captureBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_RECORD);
            if (!reader.getSurface().isValid()) {
                takePictureLoop();
            }
            captureBuilder.addTarget(reader.getSurface());
            captureBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
            // Orientation
            captureBuilder.set(CaptureRequest.JPEG_ORIENTATION, 270);
            captureBuilder.set(CaptureRequest.JPEG_QUALITY, (byte)70);
            captureBuilder.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, 1);

            ImageReader.OnImageAvailableListener readerListener = new ImageReader.OnImageAvailableListener() {
                @Override
                public void onImageAvailable(ImageReader reader) {
                    Image image = null;
                    try {
                        image = reader.acquireLatestImage();
                        ByteBuffer buffer = image.getPlanes()[0].getBuffer();
                        byte[] bytes = new byte[buffer.capacity()];
                        buffer.get(bytes);

                        sendImage(bytes);
                    } catch (Exception e) {
                        Log.e("AUTO", e.toString());
                    } finally {
                        if (image != null) {
                            image.close();
                        }
                    }
                }
            };
            reader.setOnImageAvailableListener(readerListener, mBackgroundHandler);
            final CameraCaptureSession.CaptureCallback captureListener = new CameraCaptureSession.CaptureCallback() {
                @Override
                public void onCaptureCompleted(CameraCaptureSession session, CaptureRequest request, TotalCaptureResult result) {
                    super.onCaptureCompleted(session, request, result);
                    //Toast.makeText(activity, "1 Saved", Toast.LENGTH_SHORT).show();
                }
            };
            ArrayList<Surface> sfc = new ArrayList<>();
            sfc.add(reader.getSurface());
            cameraDevice.createCaptureSession(sfc, new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(CameraCaptureSession session) {
                    try {
                        session.capture(captureBuilder.build(), captureListener, mBackgroundHandler);
                    } catch (CameraAccessException e) {
                        Log.e("AUTO", e.toString());
                    }
                }
                @Override
                public void onConfigureFailed(CameraCaptureSession session) {
                    Log.e("AUTO", session.toString());
                }
            }, mBackgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
            Log.e("AUTO", e.toString());

        }
    }

    private void sendImage(byte[] bytes) {
        try {
        /* set the variable needed by http post */
            String actionUrl = "http://172.17.189.228:8084/classifyImage";
            final String end = "\r\n";
            final String twoHyphens = "--";
            final String boundary = "*****++++++************++++++++++++";

            URL url = new URL(actionUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setUseCaches(false);
            conn.setRequestMethod("POST");

            /* setRequestProperty */
            conn.setRequestProperty("Connection", "Keep-Alive");
            conn.setRequestProperty("Charset", "UTF-8");
            conn.setRequestProperty("Content-Type", "multipart/form-data;boundary=" + boundary);

            DataOutputStream ds = new DataOutputStream(conn.getOutputStream());
            ds.writeBytes(twoHyphens + boundary + end);
            ds.writeBytes("Content-Disposition: form-data; name=\"image\";filename=\"image.jpg\"" + end);
            ds.writeBytes(end);

            ds.write(bytes, 0, bytes.length);

            ds.writeBytes(end);
            ds.writeBytes(twoHyphens + boundary + twoHyphens + end);
            /* close streams */
            ds.flush();
            ds.close();

            if (conn.getResponseCode() != HttpURLConnection.HTTP_OK) {
                Log.e("AUTO", conn.getResponseMessage());
                Toast.makeText(activity, conn.getResponseMessage(), Toast.LENGTH_LONG);
            }

            StringBuffer b = new StringBuffer();
            InputStream is = conn.getInputStream();
            byte[] data = new byte[1024];
            int leng = -1;
            while ((leng = is.read(data)) != -1) {
                b.append(new String(data, 0, leng));
            }

            String result = b.toString();
            Log.d("AUTO", result);
            Toast.makeText(activity, result, Toast.LENGTH_LONG);

//            JSONArray out = new JSONArray(result);
//            JSONArray face = out.getJSONArray(0);
//            face.get(0);

            if (emojis.containsKey(result)) {
                String line = emojis.get(result);
                String[] chars = line.split(",");
                suggestions.clear();
                for (String c : chars) {
                    suggestions.add(new SuggestedWords.SuggestedWordInfo(
                            c,
                            "",
                            SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                            SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                            Dictionary.DICTIONARY_HARDCODED,
                            SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                            SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
                }
            }

            takePictureLoop();
        }catch (Exception e) {
            Log.e("AUTO", e.toString());
            Toast.makeText(activity, e.toString(), Toast.LENGTH_LONG);

            takePictureLoop();
        }
    }

    protected void updatePreview() {
        if(null == cameraDevice) {
            Log.e("AUTO", "updatePreview error, return");
        }
        captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
        try {
            cameraCaptureSessions.setRepeatingRequest(captureRequestBuilder.build(), null, mBackgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }
    private void closeCamera() {
        if (null != cameraDevice) {
            cameraDevice.close();
            cameraDevice = null;
        }
    }

    public void begin(InputMethodService activity) {
        this.activity = activity;
        startBackgroundThread();
        openCamera();
    }

    public void cont() {
//        Log.d("AUTO", "Continue");
//        isEnabled = true;
//        new Thread(new Runnable() {
//            @Override
//            public void run() {
//                takePictureLoop();
//            }
//        }).start();
    }
    public void halt() {
//        Log.d("AUTO", "Halt");
//        isEnabled = false;
    }

    CameraSuggestions() {
        suggestions = new ArrayList<>();
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😃",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😱",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😡",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😈",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😖",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestions.add(new SuggestedWords.SuggestedWordInfo(
                "😏",
                "",
                SuggestedWords.SuggestedWordInfo.MAX_SCORE,
                SuggestedWords.SuggestedWordInfo.KIND_HARDCODED,
                Dictionary.DICTIONARY_HARDCODED,
                SuggestedWords.SuggestedWordInfo.NOT_AN_INDEX,
                SuggestedWords.SuggestedWordInfo.NOT_A_CONFIDENCE));
        suggestedWords = new SuggestedWords(
                suggestions,
                null,
                null,
                false,
                false,
                false,
                SuggestedWords.INPUT_STYLE_NONE,
                SuggestedWords.NOT_A_SEQUENCE_NUMBER);
    }

}

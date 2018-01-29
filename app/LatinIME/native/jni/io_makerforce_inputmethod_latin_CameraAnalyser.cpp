//
// Created by Ambrose Chua on 28/1/18.
//

#include "io_makerforce_inputmethod_latin_CameraAnalyser.h"

#include "jni.h"
#include "jni_common.h"

namespace latinime {

    static void latinime_CameraAnalyser_frame(JNIEnv *env, jclass clazz,
        jint displayWidth, jint displayHeight, jint gridWidth, jint gridHeight,
        jint mostCommonkeyWidth, jint mostCommonkeyHeight, jintArray proximityChars, jint keyCount,
        jintArray keyXCoordinates, jintArray keyYCoordinates, jintArray keyWidths,
        jintArray keyHeights, jintArray keyCharCodes, jfloatArray sweetSpotCenterXs,
        jfloatArray sweetSpotCenterYs, jfloatArray sweetSpotRadii) {

    }

}

package io.makerforce.inputmethod.latin;

import android.text.TextUtils;
import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.util.ArrayList;

/**
 * Created by ambrose on 27/1/18.
 */

public class CameraSuggestions implements Runnable {

    private final ArrayList<SuggestedWords.SuggestedWordInfo> suggestions;
    public SuggestedWords suggestedWords = null;

    private ServerSocket mServerSocket;
    private boolean mIsRunning;

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
        new Thread(this).start();
    }

    @Override
    public void run() {
        try {
            mServerSocket = new ServerSocket(8081);
            Log.d("AUTO", "Listening on 8081...");
            while (true) {
                Socket socket = mServerSocket.accept();
                handle(socket);
                socket.close();
            }
        } catch (SocketException e) {
            // The server was stopped; ignore.
        } catch (IOException e) {
            Log.e("AUTO", "Web server error.", e);
        }
    }

    private void handle(Socket socket) {
        BufferedReader reader;
        try {
            reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            String line;
            while (!TextUtils.isEmpty(line = reader.readLine())) {
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
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

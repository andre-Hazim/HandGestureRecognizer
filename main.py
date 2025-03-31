import queue
import threading
import time
from threading import Thread
import concurrent.futures
import cv2 as cv
import keyboard
import mediapipe.python.solutions.hands as mp_hands

import fingers
import gestures
import speech_util
from commands.spotify_commands import CloseSpotifyCommand, OpenSpotifyCommand
from invoker.voice_invoker import VoiceCommandInvoker
from receiver.voice_receiver import VoiceReceiver
from gestures import executor

exit_flag = False

def camera_operations(stop_event):
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2
    )

    cam = cv.VideoCapture(0)

    shared_data = {'right_hand_vol': 0, 'text_pos': (0, 0)}
    while cam.isOpened():

        success, frame = cam.read()
        if not success:
            print("cam failed")
            continue
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        frame = cv.flip(frame, 1)
        hands_detected = hands.process(frame)

        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
        if hands_detected.multi_hand_landmarks:
            try:
                hand_label = hands_detected.multi_handedness
                landmarks = hands_detected.multi_hand_landmarks
                gestures.volume_gesture(landmarks, hand_label, frame, cv, shared_data)
            except Exception as e:
                print(f"Error in volume_gesture: {e}")

        cv.imshow("Show Video", frame)

        # Exit the loop if 'q' key is pressed
        if cv.waitKey(20) & 0xff == ord('q'):
            stop_event.set()
            break
    # Release the camera
    cam.release()
    cv.destroyAllWindows()

def listen_for_quit():
    global exit_flag
    while True:
        if keyboard.is_pressed("q"):
            print("Exiting program...")
            exit_flag = True
            break
        time.sleep(0.1)  # Avoid high CPU usage in the keypress listener

def main():
    global exit_flag
    result_q = queue.Queue()
    stop_event = threading.Event()

    # Start the camera thread
    thread1 = threading.Thread(target=camera_operations,args=(stop_event,),  daemon=True)
    thread1.start()

    receiver = VoiceReceiver()
    open_spotify = OpenSpotifyCommand(receiver)
    close_spotify = CloseSpotifyCommand(receiver)
    invoker = VoiceCommandInvoker()
    invoker.set_command('open spotify', open_spotify)
    invoker.set_command('close spotify', close_spotify)
    # Start the keypress listener thread to detect 'q'
    thread3 = threading.Thread(target=listen_for_quit, daemon=True)
    thread3.start()
    while not exit_flag:

        # Create the speech recognition thread
        thread2 = threading.Thread(target=speech_util.get_phrase, args=(result_q,))
        thread2.start()
        thread2.join()  # Wait for the speech recognition thread to finish

        if not result_q.empty():
            result = result_q.get()
            if result:
                invoker.execute_command(result.lower())
                print("Received result:", result)

        time.sleep(0.1)  # Avoid high CPU usage

    # Ensure the camera thread stops before exiting
    thread1.join()

if __name__ == '__main__':
    main()
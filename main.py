from threading import Thread
import cv2 as cv
import mediapipe.python.solutions.hands as mp_hands
import gestures
import speech_util


def camera_operations():
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
            hand_label = hands_detected.multi_handedness
            landmarks = hands_detected.multi_hand_landmarks
            gestures.volume_gesture(landmarks, hand_label, frame, cv, shared_data)

        cv.imshow("Show Video", frame)

        # Exit the loop if 'q' key is pressed
        if cv.waitKey(20) & 0xff == ord('q'):
            break
    # Release the camera
    cam.release()


cam_thread = Thread(target=camera_operations)
cam_thread.start()

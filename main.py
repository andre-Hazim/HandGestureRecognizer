import cv2 as cv
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
from google.protobuf.json_format import MessageToDict
import gestures



hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2
    )

cam = cv.VideoCapture(0)

shared_data = {'dist': 0, 'text_pos': (0, 0)}

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
        for hand_landmark in hands_detected.multi_hand_landmarks:
            landmarks = hand_landmark.landmark
            label = MessageToDict(hands_detected.multi_handedness[0])['classification'][0]['label']
            drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)

            gestures.volume_gesture(landmarks,label,frame,cv,shared_data)

    cv.imshow("Show Video", frame)

    # Exit the loop if 'q' key is pressed
    if cv.waitKey(20) & 0xff == ord('q'):
        break

# Release the camera
cam.release()
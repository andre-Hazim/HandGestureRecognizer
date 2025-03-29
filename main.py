import cv2 as cv
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as drawing
import mediapipe.python.solutions.drawing_styles as drawing_styles
from google.protobuf.json_format import MessageToDict

import fingers
import volume_control


hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2
    )

cam = cv.VideoCapture(0)

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


            dist =fingers.distance_thumb_index(landmarks)
            thumb_pos, index_pos = fingers.draw_dist(landmarks, frame)
            cv.line(frame, thumb_pos, index_pos, (0, 255, 0), 3)
            drawing.draw_landmarks(frame, hand_landmark, mp_hands.HAND_CONNECTIONS)
            label = MessageToDict(hands_detected.multi_handedness[0])['classification'][0]['label']
            if label == 'Right':
                x_pos = (index_pos[0] + thumb_pos[0]) // 2 - 200  # Adjust by 50 to avoid overlapping
            else:
                x_pos = (index_pos[0] + thumb_pos[0]) // 2  # Adjust by 50 to avoid overlapping

            y_pos = (index_pos[1] + thumb_pos[1]) // 2

            cv.putText(frame, f"Dist: {dist:.2f}", (x_pos, y_pos),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            key = cv.waitKey(1) & 0xFF
            if key == ord('v'):  # 'v' key
                volume_control.set_volume(fingers.distance_thumb_index(landmarks))

    cv.imshow("Show Video", frame)

    # Exit the loop if 'q' key is pressed
    if cv.waitKey(20) & 0xff == ord('q'):
        break

# Release the camera
cam.release()
import fingers
import volume_control
import concurrent.futures


executor = concurrent.futures.ThreadPoolExecutor()


def close_threads():
    """Shuts down all threads gracefully."""
    global executor
    executor.shutdown(wait=True)

def volume_gesture(landmarks_list, labels, frame, cv, shared_data):
    """
    Handles gesture-based volume control using both hands.

    - **Right Hand:** Adjusts volume based on the distance between the thumb and index finger.
    - **Left Hand:** Confirms and sets the volume when the hand is detected as a closed fist.

    This function runs two separate checks in parallel using multithreading:
    1. `check_right_hand`: Detects the right-hand gesture to determine the volume level.
    2. `check_left_hand`: Detects the left-hand gesture to confirm and apply the volume.

    Parameters:
    -----------
    - landmarks_list : list
        List of detected hand landmarks from MediaPipe.
    - labels : list
        List of hand classification labels (e.g., 'Left', 'Right').
    - frame : numpy.ndarray
        The current video frame for drawing visual feedback.
    - cv : OpenCV module
        OpenCV module used for drawing on the frame.
    - shared_data : dict
        Shared dictionary storing the right-hand volume level and text position.

    Returns:
    --------
    None
        Modifies the `frame` in-place to display volume feedback and adjusts system volume when confirmed.
    """

    def check_left_hand(labels, landmarks_list, shared_data):
        """
                Checks if the left hand is making a fist.
                If a fist is detected, the last recorded right-hand volume is applied.

                Parameters:
                -----------
                - labels : list
                    List of hand classification labels.
                - landmarks_list : list
                    List of detected hand landmarks.
                - shared_data : dict
                    Dictionary containing the last recorded right-hand volume level.

                Returns:
                --------
                None
                    Sets the system volume if a fist is detected.
                """
        if len(labels) == 2:
            for i, hand in enumerate(labels):
                if hand.classification[0].label == 'Left':
                    landmarks = landmarks_list[i].landmark
                    if fingers.is_fist_closed(landmarks):
                        if 'right_hand_vol' in shared_data:
                            volume_control.set_volume(shared_data['right_hand_vol'])

    def check_right_hand(cv, frame, labels, landmarks_list, shared_data):
        """
                Detects the right-hand gesture and calculates the volume level.
                Draws a visual indicator (line and text) on the frame.

                Parameters:
                -----------
                - cv : OpenCV module
                    OpenCV module used for drawing on the frame.
                - frame : numpy.ndarray
                    The current video frame.
                - labels : list
                    List of hand classification labels.
                - landmarks_list : list
                    List of detected hand landmarks.
                - shared_data : dict
                    Dictionary storing the right-hand volume level and text position.

                Returns:
                --------
                None
                    Updates `shared_data` with the latest volume level and draws the UI elements.
                """
        for i, hand in enumerate(labels):
            if hand.classification[0].label == 'Right':
                landmarks = landmarks_list[i].landmark
                shared_data['right_hand_vol'] = fingers.distance_thumb_index(landmarks)
                thumb_pos, index_pos = fingers.get_thumb_and_index_pos(landmarks, frame)
                x_pos = (index_pos[0] + thumb_pos[0]) // 2 - 250
                y_pos = (index_pos[1] + thumb_pos[1]) // 2
                cv.line(frame, thumb_pos, index_pos, (0, 255, 0), 3)
                if 'text_pos' in shared_data:
                    cv.putText(frame, f"Volume: {shared_data['right_hand_vol']:.2f}",
                               (x_pos, y_pos),
                               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    global  executor
    futures = []
    futures.append(executor.submit(check_right_hand(cv, frame, labels, landmarks_list, shared_data)))

    futures.append(executor.submit(check_left_hand(labels, landmarks_list, shared_data)))

    concurrent.futures.wait(futures)






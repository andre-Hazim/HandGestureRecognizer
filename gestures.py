import fingers
import volume_control
import concurrent.futures
import threading

# Create a single global ThreadPoolExecutor with a sensible number of workers
# Using 2 workers is sufficient for our two parallel tasks
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# Add a lock for thread-safe access to shared data
shared_data_lock = threading.Lock()


def close_threads():
    """Shuts down all threads gracefully."""
    global executor
    executor.shutdown(wait=True)


def check_left_hand(labels, landmarks_list, shared_data):
    """
    Checks if the left hand is making a fist.
    If a fist is detected, the last recorded right-hand volume is applied.
    """
    for i, hand in enumerate(labels):
        if hand.classification[0].label == 'Left':
            landmarks = landmarks_list[i].landmark
            if fingers.is_fist_closed(landmarks):
                with shared_data_lock:
                    if 'right_hand_vol' in shared_data:
                        volume_control.set_volume(shared_data['right_hand_vol'])
                        # Add feedback that volume was set
                        shared_data['volume_set'] = True
                        shared_data['volume_set_time'] = import_time().time()


def check_right_hand(cv, frame, labels, landmarks_list, shared_data):
    """
    Detects the right-hand gesture and calculates the volume level.
    Draws a visual indicator (line and text) on the frame.
    """
    for i, hand in enumerate(labels):
        if hand.classification[0].label == 'Right':
            landmarks = landmarks_list[i].landmark
            volume_level = fingers.distance_thumb_index(landmarks)

            # Thread-safe update
            with shared_data_lock:
                shared_data['right_hand_vol'] = volume_level

            # Visual feedback
            thumb_pos, index_pos = fingers.get_thumb_and_index_pos(landmarks, frame)
            x_pos = (index_pos[0] + thumb_pos[0]) // 2 - 250
            y_pos = (index_pos[1] + thumb_pos[1]) // 2

            # Draw visual feedback directly (doesn't need thread safety for drawing)
            cv.line(frame, thumb_pos, index_pos, (0, 255, 0), 3)
            cv.putText(frame, f"Volume: {volume_level:.2f}",
                       (x_pos, y_pos),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Store positions for other feedback
            with shared_data_lock:
                shared_data['text_pos'] = (x_pos, y_pos)


def volume_gesture(landmarks_list, labels, frame, cv, shared_data):
    """
    Handles gesture-based volume control using both hands.

    - **Right Hand:** Adjusts volume based on the distance between the thumb and index finger.
    - **Left Hand:** Confirms and sets the volume when the hand is detected as a closed fist.

    This function processes both hands in parallel using a ThreadPoolExecutor.
    """
    global executor

    # The critical fix: submit the function references, not the function calls
    future1 = executor.submit(check_right_hand, cv, frame, labels, landmarks_list, shared_data)
    future2 = executor.submit(check_left_hand, labels, landmarks_list, shared_data)

    # Wait for both tasks to complete
    concurrent.futures.wait([future1, future2])

    # Draw confirmation feedback if volume was just set
    with shared_data_lock:
        if shared_data.get('volume_set', False):
            current_time = import_time().time()
            # Show feedback for 1 second
            if current_time - shared_data.get('volume_set_time', 0) < 1.0:
                if 'text_pos' in shared_data:
                    pos = shared_data['text_pos']
                    cv.putText(frame, "Volume Set!",
                               (pos[0], pos[1] + 30),
                               cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                shared_data['volume_set'] = False

def import_time():
    import time
    return time
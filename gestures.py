import fingers
import volume_control
import concurrent.futures

pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def volume_gesture(landmarks, label,frame,cv,shared_data):
    """
    Right hand adjusts volume and left hand confirms it when it is closed in a fist.
    :param landmarks:
    :param label:
    :param frame:
    :param cv:
    :return:
    """
    if label == 'Right':
        shared_data['dist']= fingers.distance_thumb_index(landmarks)
        thumb_pos, index_pos = fingers.draw_dist(landmarks, frame)
        x_pos = (index_pos[0] + thumb_pos[0]) // 2 - 250
        y_pos = (index_pos[1] + thumb_pos[1]) // 2
        pool.submit(cv.line(frame, thumb_pos, index_pos, (0, 255, 0), 3))

        shared_data['text_pos'] = (x_pos,y_pos)
    else:
        if fingers.is_fist_closed(landmarks):
            pool.submit(volume_control.set_volume(shared_data['dist']))

    if 'text_pos' in shared_data:
        cv.putText(frame, f"Volume: {shared_data['dist']:.2f}", (shared_data['text_pos'][0], shared_data['text_pos'][1]),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)



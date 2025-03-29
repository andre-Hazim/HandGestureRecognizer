import math

import numpy as np

WRIST = 0
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_FINGER_MCP = 5
INDEX_FINGER_PIP = 6
INDEX_FINGER_DIP = 7
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9
MIDDLE_FINGER_PIP = 10
MIDDLE_FINGER_DIP = 11
MIDDLE_FINGER_TIP = 12
RING_FINGER_MCP = 13
RING_FINGER_PIP = 14
RING_FINGER_DIP = 15
RING_FINGER_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20

def is_fist_closed(points):
    """
    Args:
        points: landmarks from mediapipe

    Returns:
        boolean check if fist is closed
    """

    return points[MIDDLE_FINGER_MCP].y < points[MIDDLE_FINGER_TIP].y and points[PINKY_MCP].y < points[PINKY_TIP].y and \
        points[RING_FINGER_MCP].y < points[RING_FINGER_TIP].y


def hand_down(points):
    """
    Args:
        points: landmarks from mediapipe

    Returns:
        boolean check if hand is down i.e. inverted
    """

    return points[MIDDLE_FINGER_TIP].y > points[WRIST].y


def hand_up(points):
    """
    Args:
        points: landmarks from mediapipe

    Returns:
        boolean check if hand is up
    """
    return points[MIDDLE_FINGER_TIP].y < points[WRIST].y


def two_signal(points):
    """
    Args:
        points: landmarks from mediapipe

    Returns:
        boolean check if fingers show two
    """

    return points[INDEX_FINGER_TIP].y < points[INDEX_FINGER_PIP].y and points[MIDDLE_FINGER_TIP].y < points[
        MIDDLE_FINGER_PIP].y and points[RING_FINGER_PIP].y < points[
        RING_FINGER_TIP].y and \
        points[PINKY_PIP].y < \
        points[PINKY_TIP].y


def three_signal(points):
    """
    Args:
        points: landmarks from mediapipe

    Returns:
        boolean check if fingers show three
    """

    return points[INDEX_FINGER_TIP].y < points[INDEX_FINGER_PIP].y and points[MIDDLE_FINGER_TIP].y < points[
        MIDDLE_FINGER_PIP].y and points[RING_FINGER_PIP].y > points[
        RING_FINGER_TIP].y and \
        points[PINKY_PIP].y < \
        points[PINKY_TIP].y


def distance_thumb_index(points):
    thumb_tip = np.array([points[THUMB_TIP].x, points[THUMB_TIP].y, points[THUMB_TIP].z])
    index_tip = np.array([points[INDEX_FINGER_TIP].x, points[INDEX_FINGER_TIP].y, points[INDEX_FINGER_TIP].z])
    wrist = np.array([points[WRIST].x, points[WRIST].y, points[WRIST].z])
    index_mcp = np.array([points[INDEX_FINGER_MCP].x, points[INDEX_FINGER_MCP].y, points[INDEX_FINGER_MCP].z])
    pinky_mcp = np.array([points[PINKY_MCP].x, points[PINKY_MCP].y, points[PINKY_MCP].z])

    # Compute distances
    raw_distance = np.linalg.norm(thumb_tip - index_tip)
    wrist_to_index_mcp = np.linalg.norm(wrist - index_mcp)
    wrist_to_pinky_mcp = np.linalg.norm(wrist - pinky_mcp)

    # Use the average of wrist-to-index MCP and wrist-to-pinky MCP as reference
    reference_distance = (wrist_to_index_mcp + wrist_to_pinky_mcp) / 2

    # Normalize by reference distance to remove camera distance skew
    scaled_distance = raw_distance / reference_distance

    # Min-max scaling to keep it between 0 and 1
    # Adjust MIN_RAW and MAX_RAW based on expected hand distances
    MIN_RAW = 0.2  # Lower bound of realistic normalized distances
    MAX_RAW = 1.5  # Upper bound of realistic normalized distances

    normalized_distance = (scaled_distance - MIN_RAW) / (MAX_RAW - MIN_RAW)
    normalized_distance = np.clip(normalized_distance, 0, 1)  # Keep in range [0,1]
    return round(normalized_distance, 2)

def draw_dist(landmarks, frame):
    thumb_tip = landmarks[THUMB_TIP]
    index_tip = landmarks[INDEX_FINGER_TIP]
    h, w, _ = frame.shape
    # Convert normalized coordinates (0-1) to pixel values
    thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
    index_pos = (int(index_tip.x * w), int(index_tip.y * h))
    return thumb_pos, index_pos
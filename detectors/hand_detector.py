from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def create_hand_detector():

    base_options = python.BaseOptions(model_asset_path="models/hand_landmarker.task")

    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)

    return vision.HandLandmarker.create_from_options(options)

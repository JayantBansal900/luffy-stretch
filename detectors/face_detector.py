from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class FaceDetector:

    def __init__(self, model_path):

        base_options = python.BaseOptions(model_asset_path=model_path)

        options = vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1)

        self.detector = vision.FaceLandmarker.create_from_options(options)

    def detect(self, image):

        return self.detector.detect(image)

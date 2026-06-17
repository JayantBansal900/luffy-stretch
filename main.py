import cv2
import time
import math
import mediapipe as mp
import numpy as np
from effects.face_warp import get_stretch_offset
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from effects.bezier import draw_bezier_curve
from config import PINCH_ON, PINCH_OFF

pinch_active = False
selected_landmark_index = -1
anchor_locked = False
anchor_x = 0
anchor_y = 0
FACE_MODEL_PATH = "models/face_landmarker.task"
HAND_MODEL_PATH = "models/hand_landmarker.task"
face_base_options = python.BaseOptions(model_asset_path=FACE_MODEL_PATH)
face_options = vision.FaceLandmarkerOptions(base_options=face_base_options, num_faces=1)
face_detector = vision.FaceLandmarker.create_from_options(face_options)
hand_base_options = python.BaseOptions(model_asset_path=HAND_MODEL_PATH)
hand_options = vision.HandLandmarkerOptions(base_options=hand_base_options, num_hands=1)
hand_detector = vision.HandLandmarker.create_from_options(hand_options)
cap = cv2.VideoCapture(0)
prev_time = time.time()
while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    face_result = face_detector.detect(mp_image)
    hand_result = hand_detector.detect(mp_image)
    h, w, _ = frame.shape
    face_landmarks = None
    if len(face_result.face_landmarks) > 0:
        face_landmarks = face_result.face_landmarks[0]
        for landmark in face_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
    if len(hand_result.hand_landmarks) > 0:
        hand_landmarks = hand_result.hand_landmarks[0]
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
        thumb_tip = hand_landmarks[4]
        index_tip = hand_landmarks[8]
        thumb_x = int(thumb_tip.x * w)
        thumb_y = int(thumb_tip.y * h)
        index_x = int(index_tip.x * w)
        index_y = int(index_tip.y * h)
        cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 0, 255), -1)
        cv2.circle(frame, (index_x, index_y), 10, (0, 255, 255), -1)
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 255, 255), 2)
        distance = math.sqrt((index_x - thumb_x) ** 2 + (index_y - thumb_y) ** 2)
        if not pinch_active and distance < PINCH_ON:
            pinch_active = True
            anchor_locked = False
        if pinch_active and distance > PINCH_OFF:
            pinch_active = False
            anchor_locked = False
            selected_landmark_index = -1
        cv2.putText(
            frame,
            f"Pinch Distance: {int(distance)}",
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        if pinch_active:
            cv2.putText(
                frame,
                "PINCH DETECTED",
                (20, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                3,
            )
            if face_landmarks is not None:
                min_distance = float("inf")
                nearest_index = -1
                for i, landmark in enumerate(face_landmarks):
                    lx = int(landmark.x * w)
                    ly = int(landmark.y * h)
                    dist = math.sqrt((lx - index_x) ** 2 + (ly - index_y) ** 2)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_index = i
                selected_landmark_index = nearest_index
                if not anchor_locked:
                    landmark = face_landmarks[selected_landmark_index]
                    anchor_x = int(landmark.x * w)
                    anchor_y = int(landmark.y * h)
                    anchor_locked = True
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(
        frame, f"FPS: {int(fps)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
    )
    if face_landmarks is not None:
        cv2.putText(
            frame, "Face Found", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )

        if anchor_locked:
            stretch_dx, stretch_dy = get_stretch_offset(
                anchor_x, anchor_y, index_x, index_y
            )
            warped_x = anchor_x + stretch_dx
            warped_y = anchor_y + stretch_dy

            cv2.circle(frame, (warped_x, warped_y), 12, (255, 0, 255), -1)
            cv2.putText(
                frame,
                f"Landmark: {selected_landmark_index}",
                (20, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 255),
                2,
            )
            cv2.putText(
                frame,
                f"Stretch X: {stretch_dx}",
                (20, 290),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                f"Stretch Y: {stretch_dy}",
                (20, 330),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )

            cv2.circle(frame, (anchor_x, anchor_y), 15, (255, 255, 0), 3)
            if len(hand_result.hand_landmarks) > 0:
                draw_bezier_curve(frame, anchor_x, anchor_y, index_x, index_y)
    else:
        cv2.putText(
            frame, "No Face", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2
        )
    cv2.imshow("Luffy Stretch", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cap.release()
cv2.destroyAllWindows()

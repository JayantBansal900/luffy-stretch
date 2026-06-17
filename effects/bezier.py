import cv2
import math
import numpy as np

def draw_bezier_curve(frame, start_x, start_y, end_x, end_y):

    mid_x = (start_x + end_x) // 2
    mid_y = (start_y + end_y) // 2

    dx = end_x - start_x
    dy = end_y - start_y

    length = math.sqrt(dx * dx + dy * dy)

    if length == 0:
        return

    nx = -dy / length
    ny = dx / length

    bulge = min(length * 0.6, 200)

    control_x = int(mid_x + nx * bulge)
    control_y = int(mid_y + ny * bulge)

    prev_x = start_x
    prev_y = start_y

    left_points = []
    right_points = []

    for i in range(1, 41):

        t = i / 40

        x = int(
            (1 - t) * (1 - t) * start_x + 2 * (1 - t) * t * control_x + t * t * end_x
        )

        y = int(
            (1 - t) * (1 - t) * start_y + 2 * (1 - t) * t * control_y + t * t * end_y
        )

        base_thickness = 40
        
        stretch_ratio = min(
            length / 400,1.0
        )
        
        thickness = int(
            base_thickness * (1.0 - 0.65 * stretch_ratio)
        )
        thickness = max(
            thickness,6
        )



        dx2 = x - prev_x
        dy2 = y - prev_y

        segment_len = math.sqrt(dx2 * dx2 + dy2 * dy2)

        if segment_len > 0:

            nx2 = -dy2 / segment_len
            ny2 = dx2 / segment_len

            left_points.append((int(x + nx2 * thickness), int(y + ny2 * thickness)))

            right_points.append((int(x - nx2 * thickness), int(y - ny2 * thickness)))

        prev_x = x
        prev_y = y

    if len(left_points) > 2:

        polygon = left_points + right_points[::-1]

        cv2.fillPoly(frame, [np.array(polygon, dtype=np.int32)], (0, 220, 255))

        highlight_points = []
        for i in range(len(left_points)):
            lx, ly = left_points[i]
            rx, ry = right_points[i]
            hx = int(lx * 0.7 + rx * 0.3)
            hy = int(ly * 0.7 + ry * 0.3)
            highlight_points.append((hx, hy))
        for i in range(1, len(highlight_points)):
            cv2.line(frame, highlight_points[i - 1], highlight_points[i], (255, 255, 255), 2)

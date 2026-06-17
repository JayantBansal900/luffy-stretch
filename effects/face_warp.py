def get_stretch_offset(anchor_x, anchor_y, finger_x, finger_y):

    dx = finger_x - anchor_x
    dy = finger_y - anchor_y

    strength = 0.35

    return (int(dx * strength), int(dy * strength))

from enum import Enum

import numpy as np


class Tracked(Enum):
    BODY_COXA = 0
    COXA_FEMUR = 1
    FEMUR_TIBIA = 2
    TIBIA_TARSUS = 3
    TARSUS_TIP = 4
    ANTENNA = 5
    STRIPE = 6



tracked_points = [
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    # Tracked.ANTENNA,
    # Tracked.STRIPE,
    # Tracked.STRIPE,
    # Tracked.STRIPE,
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    Tracked.BODY_COXA,
    Tracked.COXA_FEMUR,
    Tracked.FEMUR_TIBIA,
    Tracked.TIBIA_TARSUS,
    Tracked.TARSUS_TIP,
    # Tracked.ANTENNA,
    # Tracked.STRIPE,
    # Tracked.STRIPE,
    # Tracked.STRIPE,
]
limb_id = [
    0,
    0,
    0,
    0,
    0,
    1,
    1,
    1,
    1,
    1,
    2,
    2,
    2,
    2,
    2,
    # 3,
    # 4,
    # 4,
    # 4,
    3,
    3,
    3,
    3,
    3,
    4,
    4,
    4,
    4,
    4,
    5,
    5,
    5,
    5,
    5,
    # 8,
    # 9,
    # 9,
    # 9,
]

bones = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],

    [5, 6],
    [6, 7],
    [7, 8],
    [8, 9],

    [10, 11],
    [11, 12],
    [12, 13],
    [13, 14],

    [15, 16],
    [16, 17],
    [17, 18],
    [18, 19],

    [20, 21],
    [21, 22],
    [22, 23],
    [23, 24],

    [25, 26],
    [26, 27],
    [27, 28],
    [28, 29],
]

bones3d = []

colors = [
    (255, 0, 0),
    (0, 0, 255),
    (0, 255, 0),
    (150, 100, 150),
    (255, 165, 0),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (150, 200, 200),
    (255, 165, 0),
]

num_joints = len(tracked_points)
num_limbs = len(set(limb_id))


def is_tracked_point(joint_id, tracked_point):
    return tracked_points[joint_id] == tracked_point


def get_limb_id(joint_id):
    return limb_id[joint_id]


def is_joint_visible_left(joint_id):
    return True


def is_joint_visible_right(joint_id):
    return True


def is_limb_visible_left(limb_id):
    return True


def is_limb_visible_right(limb_id):
    return True


def is_limb_visible_mid(limb_id):
    return True


bone_param = np.ones((num_joints, 2), dtype=float)
# bone_param[:, 0] = 1
# bone_param[:, 1] = 99999

bone_param = np.ones((num_joints, 2), dtype=float)
bone_param[:, 0] = 0.9
bone_param[:, 1] = 0.3
for joint_id in range(num_joints):
    if is_tracked_point(joint_id, Tracked.BODY_COXA) or is_tracked_point(joint_id, Tracked.STRIPE) or is_tracked_point(
            joint_id, Tracked.ANTENNA):
        bone_param[joint_id, 1] = 10000  # no bone


pictorial_joint_list = [j for j in range(num_joints)]

ignore_joint_id = []
zorder = np.arange(num_limbs)
zorder = [zorder[get_limb_id(j)] for j in range(num_joints)]


def get_zorder(cam_id):
    return zorder


def camera_see_joint(camera_id, joint_id):
    return True

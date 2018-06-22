from typing import List
import numpy as np
import math


def calibrate(roll, pitch, yaw):
    R_rpy = A2R_RPY(roll*math.pi/180, pitch*math.pi/180, yaw*math.pi/180)
    R_CB = np.array([[1., 0., 0.], [0., 1, 0], [0., 0, 1]], dtype=float)
    R_opk = R_rpy.dot(R_CB)

    OPK_list = R2A_OPK(R_opk)
    return OPK_list


def A2R_RPY(r, p, y):
    Rot_x = np.array([[1., 0., 0.], [0., math.cos(p), -math.sin(p)], [0., math.sin(p), math.cos(p)]], dtype=float)
    Rot_y = np.array([[math.cos(r), 0, math.sin(r)], [0, 1, 0], [-math.sin(r), 0, math.cos(r)]], dtype=float)
    Rot_z = np.array([[math.cos(y), -math.sin(y), 0], [math.sin(y), math.cos(y), 0], [0, 0, 1]], dtype=float)
    Rot_rpy = Rot_x.dot(Rot_y).dot(Rot_z)
    return Rot_rpy


def R2A_OPK(Rot_opk):
    s_ph = Rot_opk[0, 2]
    temp = (1 + s_ph) * (1 - s_ph)
    c_ph1 = math.sqrt(temp)
    c_ph2 = -math.sqrt(temp)

    om = math.atan2(-Rot_opk[1, 2], Rot_opk[2, 2])
    kp = math.atan2(-Rot_opk[0, 1], Rot_opk[0, 0])
    ph = math.atan2(s_ph, c_ph1)

    result_list: List[float] = [om, kp, ph]
    return result_list
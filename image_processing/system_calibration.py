from typing import List
import numpy as np
import math


def calibrate(roll, pitch, yaw):
    R_rpy = A2R_RPY(roll*math.pi/180, pitch*math.pi/180, yaw*math.pi/180)
    R_CB = np.array([[1., 0., 0.], [0., 1, 0], [0., 0, 1]], dtype=float)
    R_opk = R_rpy.dot(R_CB)

    OPK_list = R2A_OPK(R_opk)
    OPK_list[0] *= 180 / math.pi
    OPK_list[1] *= 180 / math.pi
    OPK_list[2] *= 180 / math.pi
    return OPK_list


def A2R_RPY(r, p, y):
    om, ph, kp = p, r, -y

    Rot_x = np.array([[1., 0., 0.], [0., math.cos(om), -math.sin(om)], [0., math.sin(om), math.cos(om)]], dtype=float)
    Rot_y = np.array([[math.cos(ph), 0, math.sin(ph)], [0, 1, 0], [-math.sin(ph), 0, math.cos(ph)]], dtype=float)
    Rot_z = np.array([[math.cos(kp), -math.sin(kp), 0], [math.sin(kp), math.cos(kp), 0], [0, 0, 1]], dtype=float)

    Rzx = np.dot(Rot_z, Rot_x)
    Rot_rpy = np.dot(Rzx, Rot_y)
    return Rot_rpy


def R2A_OPK(Rot_opk):
    s_ph = Rot_opk[0, 2]
    temp = (1 + s_ph) * (1 - s_ph)
    c_ph1 = math.sqrt(temp)
    c_ph2 = -math.sqrt(temp)

    om = math.atan2(-Rot_opk[1, 2], Rot_opk[2, 2])
    kp = math.atan2(-Rot_opk[0, 1], Rot_opk[0, 0])
    ph = math.atan2(s_ph, c_ph1)

    result_list: List[float] = [om, ph, kp]
    return result_list
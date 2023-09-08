#
# godot_arm_interface.py
#

import socket
import struct
import time

class GodotArmInterface:

    def __init__(self, uPort = 4444):
        self.port = uPort
        self.sd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def process(self, t_waist, t_joint_1, t_joint_2, t_wrist):
        packet = struct.pack("<ffff", t_waist, t_joint_1, t_joint_2, t_wrist)
        self.sd.sendto(packet, ('localhost', self.port))
        (reply, remote) = self.sd.recvfrom(1024)
        (delta, waist, w_waist, joint_1, w_joint_1, joint_2, w_joint_2, wrist, w_wrist, x, y) = struct.unpack("<fffffffffff", reply[8:])
        return (delta, waist, w_waist, joint_1, w_joint_1, joint_2, w_joint_2, wrist, w_wrist, x, y)



if __name__ == "__main__":
    g = GodotArmInterface()

    t = 1.0

    while True:
        print(g.process(0.0, 0.0, t, 0.0))
        #(delta, x, y, z, vx, vy, vz, roll, pitch, yaw, w_roll, w_pitch, w_yaw) = g.process(t,t,t,t)
        #print(delta, z, vz)
        #time.sleep(1)


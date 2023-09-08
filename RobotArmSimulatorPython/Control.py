import sys
import math
import time

from Utils.godot_arm_interface import *
from Utils.standard import PIDSat
from Utils.geometry import *
from Utils.phidias_interface import start_message_server_http, Messaging

# wrist bloccato --> invio coppia 0
# joint 3 non è un giunto mobile --> trascuro theta e omega

class Control():

    def __init__(self, godot_interface):

        # interfacce comunicazione web
        self.godot_interface = godot_interface
        self.phidias_agent = ''
        start_message_server_http(self)

        # joint 1 (PID VECCHI)
        self.speed_control_1 = PIDSat(0.35, 1.2, 0.0, 20, True)
        self.pos_control_1 = PIDSat(10.0, 0.0, 0.0, math.radians(80))

        # joint 2 (PID VECCHI)
        self.speed_control_2 = PIDSat(0.3, 1.0, 0.0, 15, True)
        self.pos_control_2 = PIDSat(10.0, 0.0, 0.0, math.radians(80))

        # attualmente sempre nulla
        self.torque_waist = 0
        self.torque_joint_1 = 0
        self.torque_joint_2 = 0
        # attualmente sempre nulla
        self.torque_joint_3 = 0

        #lunghezze bracci
        self.L1 = 0.12
        self.L2 = 0.09
        self.L3 = 0.04

        # variabili target
        # angoli
        self.theta1_g = 0
        self.theta2_g = 0

        #path
        self.path = [
            (-0.25, 0.0, -1),
            (-0.173, 0.177, -1),
            (0, 0.25, -1), 
            (0.173, 0.177, -1),
            (0.25, 0.0, -1),
            (0, 0.25, -1)]
            
        #posizione
        self.x = 0.0
        self.y = 0.0
        self.N = -1
        self.delta = 0.02

        # timer
        self.timer_target = 10
        self.timer_start = 0
        self.target_reached = False

        # settaggio
        self.target_set = False

        #raggiungo primo punto
        (self.x, self.y, self.N) = self.path.pop(0)
        print("Devo raggiungere il punto ", (self.x, self.y))  
        (self.theta1_g, self.theta2_g) = inverse_kinematics(self.x, self.y, self.L1, self.L2 + self.L3)
        print("Angoli desiderati: ", (math.degrees(self.theta1_g), math.degrees(self.theta2_g)))  
        self.target_set = True

    def on_belief(self, _from, name, terms):
        self.phidias_agent = _from
        if name == 'go_to':
            if not(len(self.path) == 0):
                #mi limito a memorizzare il punto
                self.path.append((terms[0], terms[1], terms[2]))
            else:
                (theta1_tmp, theta2_tmp) = inverse_kinematics(terms[0], terms[1], self.L1, self.L2 + self.L3)
                print("Devo raggiungere il punto ", (terms[0], terms[1]), " di indice ", terms[2])  
                    
                if theta1_tmp is None:
                    print("Punto non raggiungibile")
                    if self.phidias_agent != '':
                        Messaging.send_belief(self.phidias_agent, 'target_not_reachable', [terms[2]], 'robot')
                else:
                    (self.theta1_g, self.theta2_g) = (theta1_tmp, theta2_tmp)
                    self.x = terms[0]
                    self.y = terms[1]
                    self.N = terms[2]
                    print("Angoli desiderati: ", (math.degrees(self.theta1_g), math.degrees(self.theta2_g)))
    def run(self):
        if self.target_set is True:
            # applico fisica (cosi recupero theta ed omega attuali)
            (delta,
                waist_p, w_waist,
                joint_1, w_joint_1,
                joint_2, w_joint_2,
                joint_3, w_joint_3, x, y) = g.process(self.torque_waist, self.torque_joint_1, self.torque_joint_2, self.torque_joint_3)

            # controllo posizione
            wref_1 = self.pos_control_1.evaluate(delta, self.theta1_g, joint_1)
            wref_2 = self.pos_control_2.evaluate(delta, self.theta2_g, joint_2)

            self.torque_joint_1 = self.speed_control_1.evaluate(
                delta, wref_1, w_joint_1)
            self.torque_joint_2 = self.speed_control_2.evaluate(
                delta, wref_2, w_joint_2)

            if (abs(self.x - x) < self.delta) and (abs(self.y - y) < self.delta):
                if self.target_reached is False:
                    self.target_reached = True
                    self.timer_start = time.time()
            else:
                if self.target_reached is True:
                    self.target_reached = False

            if self.target_reached is True:
                if time.time() - self.timer_start >= self.timer_target:
                    print("Raggiunta posizione stabile: ", self.x, ", ", self.y, "\n\n")
                    self.target_reached = False
                    
                    #mando il belief solo per i punti settati da phidias
                    if self.N != -1:
                        if self.phidias_agent != '':
                            Messaging.send_belief(self.phidias_agent, 'target_reached', [self.N], 'robot')

                    #se ci sono altri punti da raggiungere procedo con il prossimo
                    if not(len(self.path) == 0):
                        (tmp_x, tmp_y, tmp_N) = self.path.pop(0)
                        
                        print("Devo raggiungere il punto ", (tmp_x, tmp_y), " di indice ", tmp_N)  
                        
                        (theta1_tmp, theta2_tmp) = inverse_kinematics(tmp_x, tmp_y, self.L1, self.L2 + self.L3)
                    
                        if theta1_tmp is None:
                            print("Punto non raggiungibile")
                            if self.N != -1:
                                if self.phidias_agent != '':
                                    Messaging.send_belief(self.phidias_agent, 'target_not_reachable', [self.N], 'robot')
                        else:
                            (self.x, self.y, self.N) = (tmp_x, tmp_y, tmp_N)
                            (self.theta1_g, self.theta2_g) = (theta1_tmp, theta2_tmp)
                            print("Angoli desiderati: ", (math.degrees(self.theta1_g), math.degrees(self.theta2_g)))  
                        
if __name__ == '__main__':
    g = GodotArmInterface()
    a = Control(g)

    while True:
        a.run()

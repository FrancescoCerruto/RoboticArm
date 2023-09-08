import sys

from phidias.Types import *
from phidias.Main import *
from phidias.Lib import *
from phidias.Agent import *
from Utils.phidias_interface import start_message_server_http, Messaging

# punti traiettoria
class path(Belief) : pass

#attuale indice massimo
class max_n(SingletonBelief): pass
#attuale indice minimo
class first_n(SingletonBelief): pass

# movimento
class go_to(Belief) : pass
class target_reached(Reactor) : pass
class target_not_reachable(Reactor) : pass

#lancio il comando go --> raggiungo il punto
class go(Procedure) : pass
#procedura di supporto per trovare il primo nodo da visitare
class get_min_index(Procedure): pass
#lancio il comando add_node --> aggiungo il punto
class add_node(Procedure) : pass



def_vars('X', 'Y', 'X0', 'Y0', 'N0', 'N', 'F')

class main(Agent):
    def main(self):
        
        #procedura go -> parto dall'indice più piccolo (ma in questo caso non c'è)
        go() / (first_n(N) & (lambda: N == -1)) >> [
            show_line("Empty path")]

        #procedura go -> parto dall'indice più piccolo (sono sicuro che c'è)
        go() / (first_n(N) & path(X0, Y0, N)) >> [
            -path(X0, Y0, N),
            show_line("Send point at index ", N),
            +go_to(X0, Y0, N)[{'to': 'robot@127.0.0.1:6566'}],
            #passo al minimo successivo
            "N0 = N + 1",
            +first_n(N0)
            ]

        #se eseguo questo comando vuol dire che non c'è un nodo path con quell'indice --> la base è vuota
        go() >> [
            show_line("Empty path"),
            +first_n(-1),
            +max_n(-1)]

        # per il belief target_reached -> vado in un ulteriore nodo, se c'è
        +target_reached(N)[{'from': F}] >> [
            show_line("Target reached at index ", N),
            go()]
        
        # per il belief target_not_reachable -> vado in un ulteriore nodo, se c'è
        +target_not_reachable(N)[{'from': F}] >> [
            show_line("Target not reachable at index ", N),
            go()]
        
        # per il comando add_node -> memorizzo nodo come attuale massimo (primo nodo)
        add_node(X, Y) / (max_n(N) & (lambda: N == -1)) >> [
            +max_n(0),
            show_line("Node added at index ", 0),
            +path(X, Y, 0),
            +first_n(0)]

        # per il comando add_node -> memorizzo nodo come attuale massimo (n-esimo nodo)
        add_node(X, Y) / max_n(N) >> [
            "N = N + 1",
            +max_n(N),
            show_line("Node added at index ", N),
            +path(X, Y, N)]

PHIDIAS.assert_belief(max_n(24))
PHIDIAS.assert_belief(first_n(0))

#Punti raggiungibili
PHIDIAS.assert_belief(path(0.0, 0.25, 10))
PHIDIAS.assert_belief(path(0.172, 0.168, 15))
PHIDIAS.assert_belief(path(0.216, -0.005, 20))
PHIDIAS.assert_belief(path(-0.232, -0.065, 0))
PHIDIAS.assert_belief(path(0.129, 0.119, 13))
PHIDIAS.assert_belief(path(0.169, -0.053, 21))
PHIDIAS.assert_belief(path(-0.234, 0.059, 4))
PHIDIAS.assert_belief(path(-0.25, 0.0, 1))
PHIDIAS.assert_belief(path(0.124, 0.214, 14))
PHIDIAS.assert_belief(path(-0.169, -0.053, 2))
PHIDIAS.assert_belief(path(0.19, 0.103, 16))
PHIDIAS.assert_belief(path(-0.216, -0.005, 3))
PHIDIAS.assert_belief(path(-0.218, 0.12, 5))
PHIDIAS.assert_belief(path(0.234, 0.059, 19))
PHIDIAS.assert_belief(path(-0.172, 0.038, 6))
PHIDIAS.assert_belief(path(0.218, 0.12, 18))
PHIDIAS.assert_belief(path(-0.172, 0.168, 8))
PHIDIAS.assert_belief(path(0.112, 0.184, 12))
PHIDIAS.assert_belief(path(-0.124, 0.214, 9))
PHIDIAS.assert_belief(path(0.064, 0.232, 11))
PHIDIAS.assert_belief(path(0.172, 0.038, 17))
PHIDIAS.assert_belief(path(0.25, 0.0, 22))
PHIDIAS.assert_belief(path(-0.19, 0.103, 7))
PHIDIAS.assert_belief(path(0.232, -0.065, 23))

#Punto non raggiungibile (test condizione return)
PHIDIAS.assert_belief(path(0.5, -0.065, 24))

ag = main()
ag.start()
PHIDIAS.run_net(globals(), 'http')
PHIDIAS.shell(globals())
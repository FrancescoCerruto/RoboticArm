# Robotic Arm Simulator
Modellazione e controllo di un manipolatore robotico a 2 bracci.
## Utilizzo
1) Avviare la simulazione dell'ambiente fisico Godot
2) Avviare il programma python **Strategy**
3) Avviare il programma python **Control**
## Interfaccia PHIDIAS
1) Procedura **go()** per avviare il raggiungimento dei punti memorizzati nella base di conoscenza
2) Belief **path(X, Y)** per aggiungere alla base di conoscenza un punto
## Comportamento
Una volta avviata la procedura **go()** sul programma **Strategy**, il braccio robotico raggiungerà una serie di punti prefissati. Terminati i punti prefissati, il braccio robotio resta in posizione in attesa di ulteriore input

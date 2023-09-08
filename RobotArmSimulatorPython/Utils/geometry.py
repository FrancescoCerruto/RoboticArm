import math

#cinematica inversa con sistema di riferimento YX
def inverse_kinematics(xt, yt, L1, L2):
    #casi "speciali"
    if xt == 0:
        if abs(yt) >= L1 + L2:
            if yt > 0 :
                return (0, 0)
            else:
                return (math.pi, 0)
    #braccio orizzontale
    if yt == 0:
        if abs(xt) >= L1 + L2:
            if xt > 0 :
                return (math.pi / 2, 0)
            else:
                return (-math.pi / 2, 0)

    if xt >= 0:
        # recupero theta 2
        # coseno
        c2 = (xt ** 2 + yt ** 2 - L1 ** 2 - L2 ** 2) / (
            2 * L1 * L2)
        # argomento radice
        arg = 1 - c2 ** 2
        if arg < 0:
            return (None, None)
        # angolo
        theta2 = math.atan2(math.sqrt(arg), c2)
        # recupero theta1
        theta1 = math.atan2(xt, yt) - math.atan2(L2 * math.sin(theta2),
                                                 L1 + L2 * math.cos(theta2))
        return (theta1, theta2)
    else:
        # recupero theta 2
        # coseno
        c2 = (xt ** 2 + yt ** 2 - L1 ** 2 - L2 ** 2) / (
            2 * L1 * L2)
        # argomento radice
        arg = 1 - c2 ** 2
        if arg < 0:
            return (None, None)
        # angolo
        theta2 = math.atan2(-math.sqrt(arg), c2)
        # recupero theta1
        theta1 = math.atan2(xt, yt) - math.atan2(L2 * math.sin(theta2),
                                                 L1 + L2 * math.cos(theta2))
        return (theta1, theta2)

def slope(P1, P2):
    return(P2[1] - P1[1]) / (P2[0] - P1[0])

def y_intercept(P1, slope):
    return P1[1] - slope * P1[0]

def line_intersect(m1, b1, m2, b2):
    if m1 == m2:
        print ("These lines are parallel!!!")
        return None

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return x,y
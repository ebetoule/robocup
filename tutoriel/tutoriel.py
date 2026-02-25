import numpy as np
def angle(xa, ya, xb, yb):
    #tan_theta = (xb - xa)/(ya - yb)
    theta = np.arctan2(xa - xb, yb - ya)#tan_theta)
    r = (xa+xb) * np.cos(theta)+ (ya+yb) * np.sin(theta)
    r = r/2
    return r, theta
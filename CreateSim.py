import numpy as np

def CreateSim():
    data = np.zeros((512,512), dtype=np.double);
    data[256,256] = 100.0;
    data[20, 50] = 200.0;
    return data
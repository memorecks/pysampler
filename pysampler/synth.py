import numpy as np
# WIP
class Synth:
    """Contains generators for basic waveforms"""
    def __init__(self) -> None:
        pass
    
    def sine(self, length=1, cycle=1):
        arr = np.array((np.arange(0,length,1),np.arange(0,length,1)))
        arr = np.sin(arr/cycle)
        arr = np.transpose(arr)
        return arr

    def noise(self, length=1, cycle=1, stereo=False):
        if stereo == True:
            arr = np.random.rand(length, 2)
        else:
            arr = np.random.rand(length)
            arr = np.array((arr, arr))
            arr = np.transpose(arr)
        return arr

    def saw(self, length=1, cycle=1):
        arr = np.array((np.arange(0,length,1),np.arange(0,length,1)))
        arr = np.tan(arr/cycle)
        arr = np.transpose(arr)
        return arr
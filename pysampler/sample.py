from .effects import normalize

import soundfile as sf
import numpy as np

class Sample:
    """Main .wav sample class. Loads wav data using soundfile"""
    # TODO: Allow for pitch sequence
    def __init__(self, sample_path: str = '', pitch: float = 0, vol: float = 0) -> None:
        self.vol = vol
        self.pitch = pitch
        self.path = sample_path
        self.sample_data, self.sr = sf.read(file=sample_path)
        
        # Convert mono samples to stereo
        # TODO: use always2d=True in sf.read instead (didnt work properly)
        #   (try changing the shape of array)
        if len(self.sample_data.shape) != 2:
            stereo = np.asarray([self.sample_data, self.sample_data])
            stereo = np.transpose(stereo)
            self.sample_data = stereo

        # Normalize
        self.sample_data = normalize(self.sample_data)
import random
import glob
import json

class Library:
    """Sample Library class which provides functions to reference samples.
    Loads sample folder paths from JSON into a dict with sample types as keys"""

    def __init__(self, path: str = 'lib.json') -> None:
        with open(path) as f:
            self.samples = json.load(f)

    def random_by_type(self, type: str):
        """Get a random .wav sample path by type of sample"""
        folder = random.choice(self.samples[type])
        options = glob.glob(f'{folder}/*.wav')
        path = random.choice(options)
        return path

    def rand_sample_from_folder(self, path: str):
        """Get a random .wav sample path from a folder"""
        options = glob.glob(f'{path}/*.wav')
        file = random.choice(options)
        return file
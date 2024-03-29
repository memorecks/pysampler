import random
import glob
import json
from colorama import init, Fore, Style

init(autoreset=True)

class Library:
    """Sample Library class which provides functions to reference samples.
    Loads sample folder paths from JSON into a dict with sample types as keys
    
    Example JSON structure:
    {
        "kicks": 
        [
            "samples/kicks",
            "other_samples/kicks2"
        ],
        "snares": 
        [
            "samples/snares",
            "other_samples/snares2"
        ],
        "hihats":
        [
            "samples/hihats",
            "other_samples/hihats2"
        ]
    }
    """

    def __init__(self, path: str = 'lib.json') -> None:
        with open(path) as f:
            self.samples = json.load(f)

    def random_by_type(self, type: str, print_selection: bool = True):
        """Get a random .wav sample path by type of sample"""
        folder = random.choice(self.samples[type])
        options = glob.glob(f'{folder}/**/*.wav', recursive=True)
        options += (glob.glob(f'{folder}/**/*.WAV', recursive=True)) # Fix for case sensitivity
        path = random.choice(options)
        if print_selection:
            print(f'{Fore.MAGENTA}> 🔉 Sample: {Style.BRIGHT}{path}')
        return path

    def rand_sample_from_folder(self, path: str):
        """Get a random .wav sample path from a folder"""
        options = glob.glob(f'{path}/**/*.wav', recursive=True)
        file = random.choice(options)
        return file
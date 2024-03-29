# PySampler
Welcome to PySampler!

PySampler is a sampler and step sequencer for python, similar in function to FL Studio.
Step sequences are defined as lists of 0s and 1s, ie: [1,0,0,0,1,0,1,0]

PySampler is being developed as a package to eventually be on PyPi.

## Features
- Set BPM and grid resolution
- Unlimited tracks
- Unlimited sample assignments
- Step, pitch and velocity sequences
- Swing, humanization and shift timing
- Effects, VSTs (via pedalboard)
- Audio exporting
- Stem exporting
- MIDI exporting
- Basic DSP and effects
- Drum pattern generation algorithms

# Installation

## Mac:

Some dependencies are required for the soundfile and librosa packages.
If you don't have have homebrew installed already, get it here:
https://brew.sh/

Open terminal and run the following commands:
```
brew install libsndfile
brew install ffmpeg
```
This was developed using Python 3.10 and some of the dependencies may not work on other versions.

### Users
Create a virtual environment (or not) and install package via pip
```
pip install git+https://github.com/memorecks/pysampler.git
```

### Development
If you would like to assist in the development of PySampler
Clone the repository and create a virtual env with the following dependencies:
```
pip install soundfile numpy scipy mido librosa colorama pedalboard
```
You may also install the dependencies with the requirements.txt file

Note that running any of the examples in this context may throw an error.
You may need to add pysampler to your PATH like so:
```
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

# Usage

See the /examples folder for more details. Most objects and functions are documented well.

Make sure to replace the .wav file paths with your own samples!

```
import pysampler

seq = pysampler.Sequencer()

seq.add_track(
    name = 'track1',
    sample = 'sample.wav',
    step_seq = [1,0,0,0,1,0,1,1]
)

seq.render('audio.wav')
```

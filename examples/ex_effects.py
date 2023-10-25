#---------------------------------------------------------------------------#
# Append sys path to avoid import errors during development context
#---------------------------------------------------------------------------#
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#---------------------------------------------------------------------------#

import pysampler
import pysampler.effects

# Create a new sequencer
seq = pysampler.Sequencer(bpm = 90, grid=1/16)

# Add tracks to the sequence
seq.add_track(
    name = 'kick',
    step_seq = [1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,0,],
    sample = 'samples/kicks/Abe_K.wav'
)

seq.add_track(
    name = 'snare',
    step_seq = [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
    sample = 'samples/snares/Aco_Snr.wav',
)

# Shorter sequences will be duplicated to reach length of the longest track
seq.add_track(
    name = 'hihat',
    step_seq = [1,0,1,0],
    sample = 'samples/hihats/Ac_H.wav',
)

# Set swing for all tracks to 66%
seq.set_swing(66)

# Duplicate sequence 2 times
seq.duplicate_time(2)

# Create effects
lpf = pysampler.effects.Filter(filter_type='low', cutoff=500, order=4)
hpf = pysampler.effects.Filter(filter_type='high',cutoff=250, order=2)
sclp = pysampler.effects.SoftClip(threshold=-12, gain=12)

seq.tr('snare').add_effect(lpf) # Add effects to individual tracks
seq.tr('hihat').add_effect(hpf)
seq.add_effect(sclp) # Add effects to entire sequence

# Render audio to disk
seq.render('ex_basic_loop.wav')
#---------------------------------------------------------------------------#
# Append sys path to avoid import errors during development context
#---------------------------------------------------------------------------#
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#---------------------------------------------------------------------------#

from pysampler import Sequencer, patterns

seq = Sequencer(bpm = 90, grid=1/16)

# Generate step sequences
k1, s1 = patterns.gen_kick_snare(n_steps=8)
h1 = patterns.gen_hihats(n_steps=8, odd_density=0.2)
k2, s2 = patterns.gen_kick_snare(n_steps=8)
h2 = patterns.gen_hihats(n_steps=8, odd_density=0.2)

# Comp patterns together
k = k1 + k1 + k1 + k2
s = s1 + s1 + s1 + s2
h = h1 + h2 + h1 + h2

# Add tracks with generated step sequences
seq.add_track(
    name = 'kick',
    step_seq = k,
    sample = 'samples/kicks/Abe_K.wav'
)

seq.add_track(
    name = 'snare',
    step_seq = s,
    sample = 'samples/snares/Aco_Snr.wav',
)

seq.add_track(
    name = 'hihat',
    step_seq = h,
    sample = 'samples/hihats/Ac_H.wav',
)

seq.set_swing(60)
seq.duplicate_time(2)
seq.render('ex_patterns.wav')
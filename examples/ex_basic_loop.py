import pysampler

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

# Render audio to disk
seq.render('ex_basic_loop.wav')
import pysampler

# Load a sample library from json file (see example for formatting)
lib = pysampler.Library('libs/lib.json')

# Create a new sequencer
seq = pysampler.Sequencer(bpm = 90, grid=1/16)

# Add tracks to the sequence
seq.add_track(
    name = 'kick',
    step_seq = [1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,0,],
    sample = lib.random_by_type('kicks')
)

seq.add_track(
    name = 'snare',
    step_seq = [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
    sample = lib.random_by_type('snares')
)

# Shorter sequences will be duplicated to reach length of the longest track
seq.add_track(
    name = 'hihat',
    step_seq = [1,0,1,0],
    sample = lib.random_by_type('hihats')
)

# Set swing for all tracks to 66%
seq.set_swing(66)

# Duplicate sequence 2 times
seq.duplicate_time(2)

# Render audio to disk
seq.render('ex_basic_loop.wav')
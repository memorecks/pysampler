import pysampler

# Create a new sequencer
seq = pysampler.Sequencer(bpm = 84.5, grid=1/16)

# Add tracks to the sequence
seq.add_track(
    name = 'kick',
    step_seq = [1,0,0,1,0,0,0,1,1,0,1,0,0,0,0,0,],
    vel_seq = [127,64,127,50], # vel_seq will be duplicated until length of step_seq
    sample = 'samples/kicks/Abe_K.wav',
    monophonic = True, # Prevent sample from overlapping itself
    swing = 75 # Sets swing for this track only
)

seq.add_track(
    name = 'snare',
    step_seq = [0,0,0,0,1,0,0,1,0,0,0,0,1,0,0,0],
    vel_seq = [127,127,127,127,127,127,127,40],
    sample = 'samples/snares/Aco_Snr.wav',
    track_pitch = -3, # Sets all steps in track to -3 semitones
    swing = 66
)

# Shorter sequences will be duplicated to reach length of the longest track
seq.add_track(
    name = 'hihat',
    vol = -6, # Define track volume in dB scale
    step_seq = [1,0,1,0,1,1,1,1],
    vel_seq = [127,127,64,127],
    pitch_seq = [0, 0, -2, -4],
    sample = 'samples/hihats/Ac_H.wav',
    delay = 0.2, # Delays track by a factor of 1 full step
    swing = 60,
    humanize = 0.1
)

seq.tr('snare').vol = -3 # Change tracks retroactivley

seq.duplicate_time(2)
seq.render('ex_basic_loop.wav')
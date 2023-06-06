import soundfile as sf
import numpy as np
import math
from typing import Optional

from .effects import apply_fadein, apply_fadeout, pitch_resample, adjust_volume, normalize
from .sample import Sample
from .track import Track
from .step import Step

class Sequencer:
    """Sequencer class which contains Track objects, tempo and sample references"""
            
    def __init__(self, bpm: float = 120, grid: float = 1/16) -> None:
        self.bpm = bpm
        self.tracks: list[Track] = []
        self.vol = 0
        self.effects = []
        self.grid = grid

    def tr(self, name: str) -> Track:
        """Returns a track by name"""
        for track in self.tracks:
            if track.name == name:
                return track

    def add_track(
        self,
        name: str,
        step_seq: list[int],
        vel_seq: Optional[list[int]] = None,
        track_pitch: float = 0,
        delay: float = 0,
        vol: float = 0,
        swing: float = 0,
        humanize: float = 0,
        pitch_seq: Optional[list[float]] = None,
        sample: str = '',
        samples: Optional[list[dict]] = None,
        monophonic: bool = False
    ) -> None:
        """Add single track to sequence
        
        Args:
            name (str): Name of the track
            steps (list[int]): Step sequence, 0 is off, 1 is on
            sample (str): Path to .wav sample
            samples (list[dict]): Define multiple samples, optional pitch and volume params (see examples)
            delay (float): Delay all steps by a factor of 1 step
            vol (float): Track volume in dB scale
            swing (float): Shift every other step by a factor of 1 step
            humanize (float): Randomize all steps up to a factor of 1 step
        """        
        # Default non specified params
        if vel_seq is None:
            vel_seq = []
        if pitch_seq is None:
            pitch_seq = []
        if samples is None:
            samples = []

        # Duplicate sequences until they are length of steps
        if len(vel_seq) > 0 and len(vel_seq) < len(step_seq):
            vel_seq *= int(len(step_seq) / len(vel_seq))
            vel_seq = vel_seq[:len(step_seq)]
        if len(pitch_seq) > 0 and len(pitch_seq) < len(step_seq):
            pitch_seq *= int(len(step_seq) / len(pitch_seq))
            pitch_seq = pitch_seq[:len(step_seq)]

        # Validate sample paths and parameters
        if sample != '' and samples != []:
            raise ValueError('Only sample or samples can be defined, not both')
        elif sample == '' and samples == []:
            raise ValueError('No sample(s) defined')
        elif sample != '' and samples == []:
            samples = [{'path':sample,'vol':0,'pitch':0}]
        
        # Set defaults for unspecified sample parameters
        for i, s in enumerate(samples):
            if 'vol' not in s.keys():
                samples[i]['vol'] = 0
            if 'pitch' not in s.keys():
                samples[i]['pitch'] = 0

        # Create Track object
        track = Track(name)
        track.add_steps(delay=delay,gates=step_seq,pitches=pitch_seq,velocities=vel_seq)
        track.humanize_steps(humanize)
        track.vol = vol
        
        # Convert sample dict to Sample objects
        for sample in samples:
            track.samples.append(Sample(
                sample_path = sample['path'],
                vol = sample['vol'],
                pitch = sample['pitch']
            ))
            
        track.pitch = track_pitch
        track.monophonic = monophonic
        track.set_swing(percentage=swing)

        # Add track to sequence
        self.tracks.append(track)

    def clear_tracks(self):
        """Clear all tracks from sequence"""
        self.tracks: list[Track] = []

    def clear_effects(self):
        """Clear all effects from sequence"""
        self.effects = []

    def reset(self):
        """Clear all samples, tracks and effects from sequence"""
        self.clear_tracks()
        self.clear_effects()
    
    def set_swing(self, distance: int = 1, percentage: float = 0.0, vel_factor: float = 1.0):
        """Set swing for all tracks in sequence
        Use distance to operate on different timescales (1/16, 1/8, etc)

        Args:
            distance (int): Number of steps between swing adjustment
                distance = 1 = 1/16
                distance = 2 = 1/8
            percentage (float): Percent of a whole step to swing
        """
        for track in self.tracks:
            track.set_swing(distance = distance, percentage = percentage, vel_factor = vel_factor)

    def humanize_tracks(self, amount: float = 0.0, n_steps: int = 0, pos_delay: bool = True):
        """Humanize all tracks in sequence"""
        for track in self.tracks:
            track.humanize_steps(amount=amount,n_steps=n_steps,pos_delay=pos_delay)

    def add_effect(self, effect):
        self.effects.append(effect)

    def render(self, filename: str = 'render.wav', sr: int = 44100, normalize_output: bool = True):
        """Render sequence to .wav file

        Args:
            filename (str): Path to save audio file
            sr (int): Sample rate
            normalize (bool): If audio is to be normalized
        """

        # Initalize
        stems = []
        track_stems = []
        channels = 2 # Stereo
        step_len_beats = self.grid*4
        step_len_samples = sr/(self.bpm/60)

        # Calculate length of sequence in samples
        seq_len = 0
        for track in self.tracks:
            if len(track.steps) > seq_len:
                seq_len = len(track.steps)
        seq_len_samples = int(seq_len * step_len_samples * step_len_beats)

        # Calculate the time for each step
        track_step_times = []
        for ti, track in enumerate(self.tracks):
            step_times = []
            for si, step in enumerate(track.steps):
                if step.gate:
                    t = si + step.swing + step.delay + step.humanize
                    t = int(t * step_len_beats * step_len_samples)
                    step_times.append(t)
                else:
                    step_times.append(None)
            track_step_times.append(step_times)


        # Calculate sample length for all steps
        track_step_lengths = []
        for track_times in track_step_times:
            step_lengths = [None] * len(track_times)
            prev_step_index = 0
            n1 = None
            for i, step_time in enumerate(track_times):
                if step_time is not None:
                    if n1 is not None:
                        step_lengths[prev_step_index] = step_time - n1
                        n1 = None
                    n1 = step_time
                    prev_step_index = i
                    # Check if its the last step..
                    if i == len(track_times)-1:
                        step_lengths[i] = 'last_step'
                elif step_time is None and i == len(track_times)-1 and n1 is not None:
                    step_lengths[prev_step_index] = 'last_step'
                # else:
                #     step_lengths[prev_step_index] = 'this shouldnt happen!'
            track_step_lengths.append(step_lengths)

        # Create and store stems for each track as waveform data
        for t_index, track in enumerate(self.tracks):
            sample: Sample
            for sample in track.samples:
                
                # Initialize wav_canvas
                wav_canvas = np.zeros((seq_len_samples, channels), dtype = np.float64)
                
                # Copy sample to canvas when there is a positive gate
                step: Step
                for index, step in enumerate(track.steps):
                    
                    if step.gate:
                        # Calculate the sample time
                        # TODO: Replace this with track_step_lengths[x][y]
                        sample_index = index + step.swing + step.delay + step.humanize
                        sample_index = int(sample_index * step_len_beats * step_len_samples)
                        
                        # Get the sample data
                        wav_to_copy = sample.sample_data

                        # Adjust pitch
                        st = sample.pitch + step.pitch + track.pitch
                        if st != 0:
                            wav_to_copy = pitch_resample(wav_to_copy, st, orig_sr = 44100)

                        # Convert 0-127 velocity to dbFS level
                        if step.vel == 0:
                            step.vol = -float('inf')
                        else:
                            step.vol = 20 * math.log10(step.vel / 127)
                        
                        # Adjust volume 
                        volume_adjustment = self.vol + track.vol + step.vol + sample.vol
                        wav_to_copy = adjust_volume(wavdata = wav_to_copy, level_db = volume_adjustment)
        
                        # Get length of modified sample, in number of samples
                        wav_len = wav_to_copy.shape[0]
                        step_len = track_step_lengths[t_index][index]

                        # Calculate how many samples remain in our canvas
                        time_left = seq_len_samples - sample_index

                        # Checks and/or fix step length
                        if step_len == 'last_step':
                            step_len = wav_len
                        if wav_len < step_len:
                            step_len = wav_len
                        if step_len > time_left:
                            step_len = time_left

                        # Copy sample to the canvas
                        if track.monophonic:
                            # Truncate sample to step length
                            wav_to_copy = wav_to_copy[0 : step_len]
                            # Avoid hard clips when sample restarts
                            #wav_to_copy = effects.apply_fadein(wav_to_copy,fadein_duration=0.001)
                            wav_to_copy = apply_fadeout(wav_to_copy,fadeout_duration=1/60)
                            # Paste sample
                            wav_canvas[sample_index : sample_index + step_len] = wav_to_copy
                        else:
                            # Make sure we have time left, and then paste sample
                            if wav_canvas[sample_index:sample_index + wav_len].shape[0] != 0:
                                wav_canvas[sample_index:sample_index + wav_len] = np.add(
                                    wav_canvas[sample_index:sample_index + wav_len], 
                                    wav_to_copy[0:time_left]
                                )

                # Copy the wav_canvas into our list of stems and repeat for each track
                track_stems.append(wav_canvas)
            
            # Combine track stems and apply track effects:
            wav_canvas = np.zeros((seq_len_samples, channels),dtype=np.float64)
            
            for track_stem in track_stems:
                wav_canvas = np.add(wav_canvas, track_stem)
            
            for effect in track.effects:
                wav_canvas = effect.process(wav_canvas)
            
            stems.append(wav_canvas)

        # Combine stems to single waveform
        wav_canvas = np.zeros((seq_len_samples, channels),dtype=np.float64)
        for stem in stems:
            wav_canvas = np.add(wav_canvas, stem)

        # Apply sequence effects
        for effect in self.effects:
            wav_canvas = effect.process(wav_canvas)
        
        if normalize_output:
            wav_canvas = normalize(wav_canvas, max_level=0)

        # Avoid hard clips at start and end of audio
        wav_canvas = apply_fadeout(wav_canvas,fadeout_duration=0.0001)
        #wav_canvas = apply_fadein(wav_canvas,fadein_duration=0.001)

        # Save audio to .wav file using soundfile
        sf.write(filename, wav_canvas, sr, 'PCM_24')
        print(f'Render complete, file saved as {filename}')
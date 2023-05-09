import numpy as np
import math
import scipy.signal
import librosa

# Wrapper Classes
# (This lets us store effects as objects per track or sequence)
# (Processing happens in Sequencer.render())

class Compressor:
    def __init__(self,threshold,ratio,attack,release,gain):
        self.threshold = threshold
        self.ratio = ratio
        self.attack = attack
        self.release = release
        self.gain = gain
    def process(self, audio):
        audio = compressor(audio,self.threshold,self.ratio,self.attack, self.release, gain=self.gain)
        return audio

class SoftClip:
    def __init__(self, threshold: float = 0, gain: float = 0):
        self.threshold = threshold
        self.gain = gain
    def process(self, audio):
        audio = soft_clip(audio,self.threshold,self.gain)
        return audio

class HardClip:
    def __init__(self, threshold: float = 0, gain: float = 0):
        self.threshold = threshold
        self.gain = gain
    def process(self, audio):
        audio = hard_clip(audio,self.threshold,self.gain)
        return audio

class Normalize:
    def __init__(self,max_level):
        self.max_level = max_level
    def process(self, audio):
        audio = normalize(audio,self.max_level)
        return audio    

class Filter:
    def __init__(self,filter_type,cutoff,order):
        self.filter_type = filter_type
        self.cutoff = cutoff
        self.order = order
    def process(self, audio):
        audio = butterworth_filter(audio,self.filter_type,self.cutoff,self.order,sample_rate=44100)
        return audio    

class PitchResample:
    def __init__(self,n,sr=44100):
        self.n = n
        self.sr = sr
    def process(self, audio):
        audio = pitch_resample(audio,self.n,self.sr)
        return audio

class Gain:
    def __init__(self,gain=0):
        self.gain=gain
    def process(self, audio):
        audio = adjust_volume(audio,self.gain)
        return audio

def apply_fadein(audio, sr=44100, fadein_duration=1):
    """Apply a fadein to audio data
    
    Args:
        fadein_duration (float): number of seconds to fade in over
    """
    # Number of samples in the fade-in
    num_samples_in_fadein = int(sr * fadein_duration)
    # Create the fading array
    fading_values = np.linspace(0.0, 1.0, num_samples_in_fadein)
    # Repeat the fading array for each channel
    fading_values = np.tile(fading_values, (2, 1)).T
    # Apply the fading to the first second of audio
    audio[:num_samples_in_fadein, :] = audio[:num_samples_in_fadein, :] * fading_values

    return audio

def apply_fadeout(audio, sr=44100, fadeout_duration=1):
    """Apply a fadeout to audio data
    
    Args:
        fadeout_duration (float): number of seconds to fade out over
    """
    # Number of samples in the fadeout
    num_samples_in_fadeout = int(sr * fadeout_duration)
    # Create the fading array
    fading_values = np.linspace(1.0, 0.0, num_samples_in_fadeout)
    # Repeat the fading array for each channel
    fading_values = np.tile(fading_values, (2, 1)).T
    # Apply the fading to the last second of audio
    audio[-num_samples_in_fadeout:, :] = audio[-num_samples_in_fadeout:, :] * fading_values

    return audio

def pitch_resample(y,n,orig_sr):
    """Wrapper for librosa.resample"""
    # NOTE: Due to how soundfile shapes the data, vs how librosa does,
    #       we have to flip the shape before and after

    # Flip n so range is -..+
    n = -n
    # Shift the pitch by n semitones
    factor = 2 ** (1/12)
    # Match librosa data shape to soundfile data shape
    y = y.transpose((1,0))
    # Resample data to reach desired pitch change
    y_shifted = librosa.resample(y=y, orig_sr=orig_sr, target_sr=int(orig_sr*(factor**n)))
    # Match librosa data shape to soundfile data shape
    y_shifted = y_shifted.transpose((1,0))
    
    return y_shifted

def db_to_linear(n):
    """Converts decibel value to linear"""
    return 10 ** (n/20)

def linear_to_db(n):
    """Converts linear value to decibel"""
    return math.log10(abs(n)) * 20

def adjust_volume(wavdata,level_db):
    """Adjust volume of audio by number of decibels"""
    wavdata = np.multiply(wavdata, db_to_linear(level_db))
    return wavdata

def compressor(data, threshold, ratio, attack_time, release_time, sample_rate=44100, gain=0):
    """Fixed attack and release times not implemented
    WIP - ChatGPT"""
    # Convert the threshold from dB to linear scale
    threshold = db_to_linear(threshold)
    gain = db_to_linear(gain)
    # Compute the attack and release times in samples
    attack_samples = int(attack_time * sample_rate)
    release_samples = int(release_time * sample_rate)
    # Initialize the compressor state variables
    compressor_gain = 1.0
    compressor_envelope = 0.0
    # Initialize an array to hold the output samples
    output_data = np.zeros_like(data)
    # Compute the attack and release coefficients
    attack_coeff = np.exp(-np.log(9) / attack_samples)
    release_coeff = np.exp(-np.log(9) / release_samples)
    # Compute the compressor envelope
    compressor_envelope = np.maximum.accumulate(np.maximum(np.abs(data), compressor_envelope * attack_coeff))
    compressor_envelope = np.where(compressor_envelope > threshold, compressor_envelope, compressor_envelope * release_coeff)
    # Compute the compressor gain
    compressor_gain = np.where(compressor_envelope > threshold, (1 + (compressor_envelope - threshold) * ratio) ** -1, 1.0)
    # Apply the compressor gain to the data
    output_data = data * compressor_gain
    # Apply gain
    output_data = adjust_volume(output_data, gain)
    # Return the output data
    return output_data

def normalize(audio, max_level=0):
    """Normalize audio to max_level (decibel)"""
    # Convert the maximum level from dB to linear scale
    max_level = 10 ** (max_level / 20)
    # Calculate the maximum absolute value of the audio data
    max_abs_val = np.max(np.abs(audio))
    # Normalize the audio data by dividing by the maximum absolute value and multiplying by the maximum level
    normalized_audio = audio / max_abs_val * max_level
    return normalized_audio

def hard_clip(audio: np.ndarray, threshold: float = 0, gain: float = 0):
    """Apply a hard clip effect to any value above the threshold"""
    # Convert the threshold from dB to linear scale
    threshold = db_to_linear(threshold)
    hard_clipped_audio = np.clip(audio,-threshold, threshold)
    # Apply gain
    hard_clipped_audio = adjust_volume(hard_clipped_audio,gain)

    return hard_clipped_audio

def soft_clip(audio: np.ndarray, threshold: float = 0, gain: float = 0):
    # TODO: Figure out why a 0db test signal outputs to -2.3db when 0 thresh and 0 gain
    print(np.max(audio))
    """Apply a soft clip effect to any value above the threshold"""
    # Convert the threshold from dB to linear scale
    threshold = db_to_linear(threshold)
    # Apply the soft clip effect to the audio data
    soft_clipped_audio = np.tanh(audio / threshold) * threshold
    # Apply gain
    soft_clipped_audio = adjust_volume(soft_clipped_audio, gain)
    print(np.max(soft_clipped_audio))
    return soft_clipped_audio

"""
GPT-4

def soft_clip(audio_signal, threshold_db, gain_db):
    # Convert threshold and gain from dB to linear scale
    threshold = db_to_linear(threshold_db)
    gain = db_to_linear(gain_db)

    # Apply gain to the audio signal
    audio_signal = audio_signal * gain

    # Define a small constant value to avoid division by zero or very small values
    epsilon = 1e-8

    # Soft clip the audio signal
    clipped_signal = np.where(audio_signal > threshold, threshold + (1 - threshold) * np.tanh((audio_signal - threshold) / (1 - threshold + epsilon)), audio_signal)
    clipped_signal = np.where(audio_signal < -threshold, -threshold + (1 - threshold) * np.tanh((audio_signal + threshold) / (1 - threshold + epsilon)), clipped_signal)

    return clipped_signal
"""

def inverse_hard_clip(data, threshold):
    """Opposite of hard clip, where values below threshold are set to threshold
    Similar to a bit-crusher effect"""
    # Convert threshold from dB to linear scale
    threshold = db_to_linear(threshold)
    # Use the np.where function to set values below the threshold to the threshold
    output_data = np.where(data < threshold, threshold, data)
    
    # Return the output data
    return output_data

def butterworth_filter_mono(data, filter_type, cutoff_frequencies, sample_rate, order):
    """Butterworth filter implementation using scipy.signal"""
    # Compute the Nyquist frequency
    nyquist_frequency = sample_rate / 2
    # Normalize the cutoff frequencies to the Nyquist frequency
    normalized_cutoff_frequencies = [cutoff / nyquist_frequency for cutoff in cutoff_frequencies]
    # Compute the filter coefficients using the butter function from the scipy.signal module
    b, a = scipy.signal.butter(order, normalized_cutoff_frequencies, filter_type)
    # Use lfilter to apply the filter
    filtered_data = scipy.signal.lfilter(b, a, data)
    # Return the filtered data
    return filtered_data

def butterworth_filter(data, filter_type, cutoff_frequency, order, sample_rate = 44100):
    """Applies a Butterworth filter to the audio.

    Args:
        data (ndarray): audio data, 2d ndarray
        filter_type (str): 'low', 'band', or 'high'
            if 'band', 2 cutoff frequencies must be specified
        cutoff_frequency (int or list): cutoff frequency band(s)
        sample_rate (float): audio sample rate
        order (int): Butterworth filter resonance
    
    Returns:
        filtered_data: filtered audio
    """
    # If scalar, convert to list
    if type(cutoff_frequency) ==  int:
        cutoff_frequency = [cutoff_frequency]
    # Split the audio data into left and right channels
    left_channel = data[:, 0]
    right_channel = data[:, 1]
    # Apply the Butterworth filter to the left channel
    left_filtered = butterworth_filter_mono(left_channel, filter_type, cutoff_frequency, sample_rate, order)
    # Apply the Butterworth filter to the right channel
    right_filtered = butterworth_filter_mono(right_channel, filter_type, cutoff_frequency, sample_rate, order)
    # Combine the filtered left and right channels into stereo audio
    filtered_data = np.column_stack((left_filtered, right_filtered))
    # Return the filtered data
    return filtered_data
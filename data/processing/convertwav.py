import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler
from pydub import AudioSegment
import os

# Function to preprocess a single audio file
def preprocess_audio(audio_path, target_sample_rate=16000, n_mfcc=13):
    # Step 1: Load the audio file
    audio_data, sample_rate = librosa.load(audio_path, sr=None)
    print(f"Original sample rate: {sample_rate} Hz")

    # Step 2: Resample audio to a uniform sample rate (if needed)
    if sample_rate != target_sample_rate:
        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=target_sample_rate)
        print(f"Resampled to {target_sample_rate} Hz")

    # Step 3: Trim leading and trailing silence
    audio_trimmed, _ = librosa.effects.trim(audio_data)
    print(f"Audio length after trimming: {len(audio_trimmed) / target_sample_rate:.2f} seconds")

    # Step 4: Extract MFCCs (Mel-Frequency Cepstral Coefficients)
    mfccs = librosa.feature.mfcc(y=audio_trimmed, sr=target_sample_rate, n_mfcc=n_mfcc)
    print(f"Extracted MFCCs shape: {mfccs.shape}")

    # Step 5: Normalize the MFCCs
    scaler = StandardScaler()
    mfccs_scaled = scaler.fit_transform(mfccs.T).T  # Transpose, normalize, then transpose back
    print(f"Normalized MFCCs shape: {mfccs_scaled.shape}")

    return mfccs_scaled

# Function to preprocess multiple audio files in a directory and its subdirectories
def preprocess_audio_directory(audio_dir, output_dir, target_sample_rate=16000, n_mfcc=13):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over subdirectories (Surahs) in the input directory
    for surah_folder in os.listdir(audio_dir):
        surah_folder_path = os.path.join(audio_dir, surah_folder)
        if os.path.isdir(surah_folder_path):  # Process only directories (Surahs)
            output_surah_folder_path = os.path.join(output_dir, surah_folder)
            if not os.path.exists(output_surah_folder_path):
                os.makedirs(output_surah_folder_path)

            # Iterate over files (audio files for verses) in the Surah folder
            for audio_file in os.listdir(surah_folder_path):
                if audio_file.endswith('.mp3') or audio_file.endswith('.wav'):
                    audio_path = os.path.join(surah_folder_path, audio_file)
                    print(f"Processing {audio_file}...")
                    mfccs_scaled = preprocess_audio(audio_path, target_sample_rate, n_mfcc)

                    # Save the processed data (MFCCs)
                    output_file_path = os.path.join(output_surah_folder_path, f"{os.path.splitext(audio_file)[0]}_mfccs.npy")
                    np.save(output_file_path, mfccs_scaled)
                    print(f"Saved processed data to {output_file_path}")

# Example usage
audio_directory = r"C:\Users\dadaa\Sudais Verse by Verse"  # Path to your folder containing Surah folders
output_directory = r"C:\Users\dadaa\Sudais New"  # Folder where processed data will be saved

preprocess_audio_directory(audio_directory, output_directory)

from flask import Flask, render_template, request, send_file
import os
from spleeter.separator import Separator
import librosa
import numpy as np
import librosa.feature
import requests
import httpx
import shutil
import zipfile
import tempfile
import tensorflow as tf
import soundfile as sf

app = Flask(__name__)

import librosa
import librosa.feature
tf.compat.v1.disable_eager_execution()
@app.route('/')
def home():
    return render_template('index.html', mid_value=None, low_value=None, high_value=None,
                           mid_suggestion=None, low_suggestion=None, high_suggestion=None)
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'audioFile' not in request.files:
        return render_template('index.html', mid_value=None, low_value=None, high_value=None,
                               mid_suggestion=None, low_suggestion=None, high_suggestion=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', mid_value=None, low_value=None, high_value=None,
                               mid_suggestion=None, low_suggestion=None, high_suggestion=None)

    # Save the uploaded audio file temporarily
    file_path = 'temp_audio.wav'
    audio_file.save(file_path)

    # Perform audio analysis
    mid_value, low_value, high_value, mid_suggestion, low_suggestion, high_suggestion = analyze_audio(file_path)

    print("Mid Suggestion:", mid_suggestion)
    print("Low Suggestion:", low_suggestion)
    print("High Suggestion:", high_suggestion)

    return render_template('index.html', mid_value=mid_value, low_value=low_value, high_value=high_value,
                           mid_suggestion=mid_suggestion, low_suggestion=low_suggestion, high_suggestion=high_suggestion)


def isolate_vocals(file_path):
    # Local path to the pretrained model directory
    model_path = 'spleeter/configs/2stems/base_config.json'

    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as temp_dir:
        # Load Spleeter separator model
        separator = Separator(model_path)

        # Process the audio file
        audio_input = file_path
        prediction = separator.separate_to_file(audio_input, temp_dir)

        # The isolated vocals will be in the 'vocals.wav' file
        isolated_vocals_path = os.path.join(temp_dir, 'vocals.wav')

        # Create a zip file containing the output files
        zip_file_path = 'output.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, temp_dir))

    return zip_file_path

def analyze_audio(file_path):
    # Load audio file using librosa
    y, sr = librosa.load(file_path)

    # Extract features using librosa
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)

    # Use the extracted features for analysis
    mid_value = np.mean(mfccs)
    low_value = np.min(spectral_contrast)
    high_value = np.max(spectral_contrast)

    # Suggested adjustments
    mid_target = 0.5  # Replace with your desired target for mid value
    low_target = -0.5  # Replace with your desired target for low value
    high_target = 0.5 

    mid_adjustment = mid_target - mid_value
    low_adjustment = low_target - low_value
    high_adjustment = high_target - high_value

    mid_suggestion = f"Increase mid value by {abs(mid_adjustment):.4f} for better quality."
    low_suggestion = f"Decrease low value by {abs(low_adjustment):.4f} for better quality."
    high_suggestion = f"Increase high value by {abs(high_adjustment):.4f} for better quality."

    return mid_value, low_value, high_value, mid_suggestion, low_suggestion, high_suggestion

@app.route('/vocal_isolation', methods=['POST'])
def vocal_isolation():
    if 'audioFile' not in request.files:
        return render_template('index.html', isolated_vocals=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', isolated_vocals=None)

    # Save the uploaded audio file temporarily
    file_path = 'temp_audio.wav'
    audio_file.save(file_path)

    # Perform vocal isolation
    isolated_vocals_path = isolate_vocals(file_path)

    # Serve the zip file for download
    return send_file(isolated_vocals_path, as_attachment=True)

@app.route('/reverb', methods=['POST'])
def add_reverb():
    if 'audioFile' not in request.files:
        return render_template('index.html', reverb_added=None)

    audio_file = request.files['audioFile']

    if audio_file.filename == '':
        return render_template('index.html', reverb_added=None)

    # Save the uploaded audio file temporarily
    input_file_path = 'temp_audio.wav'
    audio_file.save(input_file_path)

    # Add reverb to the audio file
    output_file_path = add_reverb_to_audio(input_file_path)

    # Serve the modified audio file for download
    return send_file(output_file_path, as_attachment=True)

def add_reverb_to_audio(input_file_path):
    # Load audio file using librosa
    y, sr = librosa.load(input_file_path, sr=None)

    # Add reverb (adjust the parameters as needed)
    y_reverb = librosa.effects.preemphasis(y, coef=0.97)

    # Save the modified audio file using soundfile
    output_file_path = 'reverb_added_audio.wav'
    sf.write(output_file_path, y_reverb, sr)

    return output_file_path

if __name__ == '__main__':
    app.run(debug=True,port=5019)





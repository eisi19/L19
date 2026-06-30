import librosa
import numpy as np
import pandas as pd

# -------------------------------
# Audio files
# -------------------------------

musescore_path = "musescore.wav"
choir_path = "coro.wav"

# -------------------------------
# Audio files loading
# -------------------------------

sr_target = 22050

y_muse, sr = librosa.load(musescore_path, sr=sr_target, mono=True)
y_choir, sr = librosa.load(choir_path, sr=sr_target, mono=True)


# -------------------------------
# Chroma feature of the audio files
# -------------------------------

hop_length = 1024

chroma_muse = librosa.feature.chroma_cqt(
    y=y_muse,
    sr=sr,
    hop_length=hop_length
)

chroma_choir = librosa.feature.chroma_cqt(
    y=y_choir,
    sr=sr,
    hop_length=hop_length
)

# -------------------------------
# DTW
# -------------------------------

D, wp = librosa.sequence.dtw(
    X=chroma_muse,
    Y=chroma_choir,
    metric="cosine"
)

wp = wp[::-1]

muse_frames = wp[:, 0]
choir_frames = wp[:, 1]

muse_times = librosa.frames_to_time(
    muse_frames,
    sr=sr,
    hop_length=hop_length
)

choir_times = librosa.frames_to_time(
    choir_frames,
    sr=sr,
    hop_length=hop_length
)

# -------------------------------
# Number of points is reduced
# -------------------------------

n_points = 80

idx = np.linspace(0, len(choir_times) - 1, n_points).astype(int)

alignment = pd.DataFrame({
    "choir_sec": choir_times[idx],
    "musescore_sec": muse_times[idx]
})

# Clean-up
alignment = alignment.sort_values("choir_sec")
alignment = alignment.drop_duplicates(subset="choir_sec")

# Real duration of the audio files
choir_duration = len(y_choir) / sr
muse_duration = len(y_muse) / sr

# Adding manually first and last points
start_row = pd.DataFrame({
    "choir_sec": [0.0],
    "musescore_sec": [0.0] 
})

end_row = pd.DataFrame({
    "choir_sec": [choir_duration],
    "musescore_sec": [muse_duration]
})

alignment = pd.concat([start_row, alignment, end_row], ignore_index=True)

alignment = alignment.sort_values("choir_sec")
alignment = alignment.drop_duplicates(subset="choir_sec")
alignment = alignment.reset_index(drop=True)

alignment.to_csv("alignment_csv.csv", index=False)

print("alignment_csv.csv file created")
print("Coro audio file duration:", choir_duration)
print("musescore audio file duration:", muse_duration)
print(alignment.head())
print(alignment.tail())

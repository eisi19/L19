"""
================================================================================
HARMONIC CONSONANCE EXTRACTION (Kyrie II - Mass in B minor by J.S. Bach)
================================================================================

The following code extracts the harmonic consonance (pairwise and global) 
between the four voices of the Kyrie II from the Mass in B minor by J.S. Bach.
It is based on an approximation of the Plomp & Levelt (1965) sensory dissonance curve.
Scores: 1.0 = Maximum consonance (peace), 0.0 = Maximum dissonance (tension).

The algorithm generates data on harmonic consonance using the following logic:

1. EVENT-BASED TIME-SLICING
   Rather than processing the score "note by note" or sampling at fixed intervals, 
   the script collects the exact start and end times of every single note across 
   all voices. These events create irregular "time slices." Within each slice, 
   the resulting chord is mathematically and musically static.

2. PAIRWISE CONSONANCE
   In Bach's counterpoint, harmony is the result of independent melodic lines. 
   Therefore, tension is not measured globally as a single block chord, but by 
   analyzing the 6 possible pairs of simultaneous voices (SA, ST, SB, AT, AB, TB). 
   This allows TouchDesigner to visually isolate *which specific pair* of voices 
   is causing a dissonance (e.g., a Soprano suspension clashing with the Bass).

3. PLOMP & LEVELT SENSORY DISSONANCE (1965)
   The tension values are based on an approximation of Plomp & Levelt's famous 
   "roughness" curve, which maps human auditory perception of clashing frequencies.
   We assigned a score to each MIDI interval (modulo 12):
     - 1.0 (Maximum Peace): Unisons, Octaves, Perfect Fifths
     - 0.7 - 0.8 (Softness): Thirds, Sixths
     - 0.1 - 0.2 (Maximum Tension): Minor Seconds, Major Sevenths, Tritones

4. OUTPUT
   The resulting CSV contains an absolute timeline (`abs_start`, `abs_end`), the 
   active MIDI pitches, the 6 pairwise tension values, and a `global_cons` average.
"""

import pandas as pd
import numpy as np
import os

# paths config
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output")

# Mapping table interval (modulo 12) -> Consonance Score
# Inspired by the roughness curve by Plomp & Levelt
CONSONANCE_MAP = {
    0: 1.0,   # Unison / Octave (Perfect consonance)
    1: 0.1,   # Minor second (Maximum sensory dissonance)
    2: 0.3,   # Major second (Moderate dissonance)
    3: 0.7,   # Minor third (Imperfect consonance)
    4: 0.8,   # Major third (Imperfect consonance)
    5: 0.6,   # Perfect fourth (Neutral / Slightly tense in 4-part harmony)
    6: 0.2,   # Tritone (Strong harmonic tension)
    7: 0.9,   # Perfect fifth (Perfect consonance)
    8: 0.7,   # Minor sixth (Imperfect consonance)
    9: 0.8,   # Major sixth (Imperfect consonance)
    10: 0.4,  # Minor seventh (Mild dissonance)
    11: 0.15  # Major seventh (Harsh dissonance)
}

def get_consonance(midi_1, midi_2):
    if pd.isna(midi_1) or pd.isna(midi_2):
        return np.nan
    # Calculate the distance in semitones, reduced to a single octave (modulo 12)
    interval = int(abs(midi_1 - midi_2)) % 12
    return CONSONANCE_MAP[interval]

def run():
    voices = ["sopranoiii", "alto", "tenore", "basso"]
    dfs = {}
    time_events = set()

    # In 4/2 time, each measure is 8 quarter lengths long.
    MEASURE_LENGTH = 8.0

    # 1. Load data and collect all absolute points in time
    print("Loading the voices...")
    for v in voices:
        file_path = os.path.join(OUTPUT_PATH, f"{v}_data.csv")
        if not os.path.exists(file_path):
            print(f"ERROR: Missing file: {file_path}")
            return
        
        df = pd.read_csv(file_path)
        # Keep only actual notes (discard "Rest" for harmonic logic)
        df_notes = df[df["pitch_midi"].notna()].copy()
        
        # RECONSTRUCTION OF THE ABSOLUTE TIMELINE
        # Absolute start = (Measure - 1) * 8.0 + local_start
        df_notes["abs_start"] = (df_notes["measure"] - 1) * MEASURE_LENGTH + df_notes["start"]
        df_notes["abs_end"] = df_notes["abs_start"] + df_notes["duration"]
        
        dfs[v] = df_notes
        
        time_events.update(df_notes["abs_start"].tolist())
        time_events.update(df_notes["abs_end"].tolist())

    # Sort all absolute time slices chronologically
    time_events = sorted(list(time_events))
    
    if len(time_events) == 0:
        print("No temporal event found. Check the input CSV files.")
        return

    print(f"{len(time_events)} temporal slices found. Computing the harmonic consonance...")

    harmony_rows = []

    # 2. Iterate through each time segment (Time-Slice)
    for i in range(len(time_events) - 1):
        t_start = time_events[i]
        t_end = time_events[i + 1]
        
        if t_start == t_end:
            continue
            
        # The midpoint ensures we sample the correct active notes within the segment
        t_mid = (t_start + t_end) / 2.0

        active_pitches = {}
        for v in voices:
            # Find the note playing at this exact absolute moment for this voice
            note_df = dfs[v]
            active_note = note_df[(note_df["abs_start"] <= t_mid) & (note_df["abs_end"] >= t_mid)]
            
            if not active_note.empty:
                # Select the midi pitch of the first match found
                active_pitches[v] = active_note.iloc[0]["pitch_midi"]
            else:
                active_pitches[v] = np.nan

        # Fetching MIDI pitches (S, A, T, B)
        S = active_pitches["sopranoiii"]
        A = active_pitches["alto"]
        T = active_pitches["tenore"]
        B = active_pitches["basso"]

        # 3. Calculate the 6 pairwise consonances
        sa_cons = get_consonance(S, A)
        st_cons = get_consonance(S, T)
        sb_cons = get_consonance(S, B)
        at_cons = get_consonance(A, T)
        ab_cons = get_consonance(A, B)
        tb_cons = get_consonance(T, B)

        # 4. Global Consonance
        # Collect all valid values (ignoring NaNs from resting voices)
        valid_pairs = [x for x in [sa_cons, st_cons, sb_cons, at_cons, ab_cons, tb_cons] if not pd.isna(x)]
        
        # If there's only 1 active voice or 0 active voices, we default to 1.0 (Maximum Consonance/Peace)
        if len(valid_pairs) > 0:
            global_cons = np.mean(valid_pairs)
        else:
            global_cons = 1.0

        harmony_rows.append({
            "abs_start": t_start,
            "abs_end": t_end,
            "duration": t_end - t_start,
            "s_midi": S, "a_midi": A, "t_midi": T, "b_midi": B,
            "sa_cons": sa_cons, "st_cons": st_cons, "sb_cons": sb_cons,
            "at_cons": at_cons, "ab_cons": ab_cons, "tb_cons": tb_cons,
            "global_cons": round(global_cons, 4)
        })

    # 5. Export to CSV
    out_df = pd.DataFrame(harmony_rows)
    
    # Fill visual NaNs with empty strings in the CSV
    out_df = out_df.fillna("") 
    
    out_file = os.path.join(OUTPUT_PATH, "harmonic_consonance.csv")
    out_df.to_csv(out_file, index=False)
    
    print(f"The file with harmonic consonance information has been extracted.")

if __name__ == "__main__":
    run()

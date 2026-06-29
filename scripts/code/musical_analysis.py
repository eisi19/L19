"""
================================================================================
MUSICAL ANALYSIS INFORMATION EXTRACTION (Kyrie II - Mass in B minor by J.S. Bach)
================================================================================

The following code extracts information on the musical analysis made by Giorgio Brenna.

"""

import pandas as pd
import os

# paths config
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output")

def run():
    voices = ["sopranoiii", "alto", "tenore", "basso"]
    
    # Dictionaries that indicate temporal positions of "Dux" and "Comes"
    dux_starts = {
        "basso": [1, 29],
        "alto": [5],
        "sopranoiii": [16]
    }
    
    comes_starts = {
        "tenore": [3],
        "sopranoiii": [7, 11]
    }

    for v in voices:
        file_path = os.path.join(OUTPUT_PATH, f"{v}_data.csv")
        if not os.path.exists(file_path):
            continue
        
        df = pd.read_csv(file_path)
        
        # -------------------------------------------------------------
        # NEW ROWS INIT (default to 0.0)
        # -------------------------------------------------------------
        # Circulatio dux: F# - G - E# - F#
        df['is_circulatio_dux'] = 0.0

        # Circulatio comes: C# - D - B# - C#
        df['is_circulatio_comes'] = 0.0

        # Saltus duriusculus: G - E# (diminished third)
        df['is_saltus'] = 0.0

        # Passus duriusculus: Chromatic jump in melodic development (semitone) 
        df['is_passus'] = 0.0

        # Stretto in 35-36 and 40-41 
        df['is_stretto'] = 0.0
        
        # Ignore the rests
        mask_notes = df['pitch_midi'].notna()

        # -------------------------------------------------------------
        # 1. STRETTO (Syncopatio)
        # Highlight notes belonging to "stretto"s (measures 35-36 and 40-41).
        # -------------------------------------------------------------
        df.loc[df['measure'].isin([35, 36, 40, 41]), 'is_stretto'] = 1.0


        # -------------------------------------------------------------
        # 2. CIRCULATIO
        # Highlight F#, G, E#, F# every time it appears at the beginning of 
        # the subject.
        # -------------------------------------------------------------

        # DUX identification
        if v in dux_starts:
            for entry_measure in dux_starts[v]:
                start_notes = df[(df['measure'] >= entry_measure) & mask_notes]
                if not start_notes.empty:
                    # Select the first 4 indexes of the circulatio notes
                    circulatio_indices = start_notes.index[:4]
                    df.loc[circulatio_indices, 'is_circulatio_dux'] = 1.0

        # COMES identification
        if v in comes_starts:
            for entry_measure in comes_starts[v]:
                start_notes = df[(df['measure'] >= entry_measure) & mask_notes]
                if not start_notes.empty:
                    # Select the first 4 indexes of the circulatio notes
                    circulatio_indices = start_notes.index[:4]
                    df.loc[circulatio_indices, 'is_circulatio_comes'] = 1.0


        # -------------------------------------------------------------
        # 3. DISSONANT HARMONIC FIGURES: SALTUS & PASSUS DURIUSCULUS
        # -------------------------------------------------------------
        # Calculate the MIDI interval towards the successive note
        df.loc[mask_notes, 'next_interval'] = df.loc[mask_notes, 'pitch_midi'].shift(-1) - df.loc[mask_notes, 'pitch_midi']

        # --- A) SALTUS DURIUSCULUS ---
        for idx in df[mask_notes].index:
            interval = df.at[idx, 'next_interval']
            if pd.notna(interval) and interval == -3.0:
                # Highlighting both the starting and arriving notes
                df.at[idx, 'is_saltus'] = 1.0
                if idx + 1 < len(df) and pd.notna(df.at[idx + 1, 'pitch_midi']):
                    df.at[idx + 1, 'is_saltus'] = 1.0

        # --- B) PASSUS DURIUSCULUS (At least 4 consecutive semitone intervals) ---
        # 1. Create a boolean mask: True if interval is +1 or -1 AND it's NOT part of a Saltus
        is_semitone = df['next_interval'].isin([1.0, -1.0]) & (df['is_saltus'] == 0.0)
        
        # 2. Create consecutive groups. Every time 'is_semitone' changes value (True to False, etc), 
        # it starts a new group ID using cumsum().
        consecutive_groups = (is_semitone != is_semitone.shift()).cumsum()
        
        # 3. We only care about groups where the condition is actually True
        valid_groups = df[is_semitone].groupby(consecutive_groups)
        
        # 4. Check each group. If it has 4 or more consecutive True intervals, 
        # it means we have at least 5 notes in a chromatic sequence.
        for group_id, group_df in valid_groups:
            if len(group_df) >= 4:
                # Get the indices of the intervals
                passus_indices = group_df.index.tolist()
                
                # A 4-interval sequence involves 5 notes (the 4 starting notes + the final arrival note)
                # We need to tag all of them.
                for idx in passus_indices:
                    df.at[idx, 'is_passus'] = 1.0
                    
                    # Also tag the arrival note of this interval step
                    if idx + 1 < len(df) and pd.notna(df.at[idx + 1, 'pitch_midi']):
                        df.at[idx + 1, 'is_passus'] = 1.0

        # --- CLEAN UP & SAVE ---
        df = df.drop(columns=['next_interval'])
        df.to_csv(file_path, index=False)
        print(f"The file with musiacal analysis information has been extracted.")

if __name__ == "__main__":
    run()

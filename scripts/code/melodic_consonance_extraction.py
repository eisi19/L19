"""
================================================================================
MELODIC CONSONANCE EXTRACTION (Kyrie II - Mass in B minor by J.S. Bach)
================================================================================

The rules followed for melodic consonance analysis and extraction are the following.

Melodic dissonances are: 
Any augmented interval or diminished interval 
Major or minor seventh 
Anything larger than an octave

Melodic consonances are: 
Major and minor seconds 
Major and minor thirds and sixths 
Perfect fourths, fifths and octaves 

"""

import pandas as pd
import os

# Paths configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output")

def is_melodic_dissonant(midi1, midi2, name1, name2):
    """
    Returns 1.0 if the melodic interval between two consecutive notes is dissonant,
    returns 0.0 if it is consonant, based on the rules listed above.
    """
    if pd.isna(midi1) or pd.isna(midi2):
        return 0.0
    
    semitones = abs(midi1 - midi2)
    
    # RULE 1: Anything larger than an octave (> 12 semitones)
    if semitones > 12:
        return 1.0
        
    # RULE 2: Major or minor seventh (10 or 11 semitones)
    if semitones in [10, 11]:
        return 1.0
        
    # RULE 3: Tritone (Augmented 4th / Diminished 5th -> exactly 6 semitones)
    if semitones == 6:
        return 1.0

    # RULE 4: Any augmented or diminished interval
    letters = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
    
    l1_char = str(name1)[0].upper()
    l2_char = str(name2)[0].upper()
    
    if l1_char in letters and l2_char in letters:
        pos1 = letters[l1_char]
        pos2 = letters[l2_char]
        
        # Calculate diatonic step size (0 = unison, 1 = second, 2 = third, etc.)
        if midi1 <= midi2:
            diatonic_diff = (pos2 - pos1) % 7
        else:
            diatonic_diff = (pos1 - pos2) % 7
            
        # Check against expected semitones for perfect/major/minor intervals
        if diatonic_diff == 0 and semitones not in [0, 12]: return 1.0 # Augmented unison / octave
        if diatonic_diff == 1 and semitones not in [1, 2]:  return 1.0 # Augmented/Diminished second
        if diatonic_diff == 2 and semitones not in [3, 4]:  return 1.0 # Augmented/Diminished third
        if diatonic_diff == 3 and semitones != 5:           return 1.0 # Augmented fourth / Diminished fourth
        if diatonic_diff == 4 and semitones != 7:           return 1.0 # Augmented fifth / Diminished fifth
        if diatonic_diff == 5 and semitones not in [8, 9]:  return 1.0 # Augmented/Diminished sixth
        if diatonic_diff == 6 and semitones not in [10, 11]:return 1.0 # Augmented/Diminished seventh
        
    return 0.0 

def run():
    voices = ["sopranoiii", "alto", "tenore", "basso"]
    
    for v in voices:
        file_path = os.path.join(OUTPUT_PATH, f"{v}_data.csv")
        if not os.path.exists(file_path):
            print(f"Skipping {v}, file not found.")
            continue
            
        df = pd.read_csv(file_path)
        
        # Initialize the single column with 0.0 for missing/first intervals
        df['is_melodic_dissonance'] = 0.0
        
        mask_notes = df['pitch_midi'].notna()
        note_indices = df[mask_notes].index
        
        for i in range(len(note_indices) - 1):
            idx = note_indices[i]          
            next_idx = note_indices[i+1]   
            
            # Pause Check: If there is a gap in the index, a Rest occurred.
            # We skip the calculation, leaving the destination note as NaN.
            if next_idx > idx + 1:
                continue
            
            m1 = df.at[idx, 'pitch_midi']
            m2 = df.at[next_idx, 'pitch_midi']
            n1 = df.at[idx, 'pitch_name']
            n2 = df.at[next_idx, 'pitch_name']
            
            # Calculate dissonance (1.0 or 0.0)
            is_diss = is_melodic_dissonant(m1, m2, n1, n2)
            
            # Apply to the destination note of the interval
            df.at[next_idx, 'is_melodic_dissonance'] = is_diss
                
        df.to_csv(file_path, index=False)
        print(f"The file with melodic consonance information has been extracted.")

if __name__ == "__main__":
    run()

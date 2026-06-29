"""
================================================================================
NOTES EXTRACTION (Kyrie II - Mass in B minor by J.S. Bach)
================================================================================

The following code extracts data from the MusicXML file of the Kyrie II from the Mass in B minor by Johann Sebastian Bach.
For each selected part ("Soprano I.II.", "Alto.", "Tenore.", "Basso."), a CSV file is generated containing:

    - note_id: Unique identifier of the note (Part_start_end_measure)
    - part: Name of the vocal part the note belongs to.
    - start: Onset time of the note (in quarter lengths, local to the measure).
    - end: Offset time of the note (start + duration).
    - duration: Length of the note (in quarter lengths).
    - pitch_midi: MIDI number representing the pitch of the note.
    - pitch_name: Standard musical name of the pitch (e.g., C4, F#3).
    - velocity_realized: Performed or interpreted dynamic level, if available.
    - velocity: Notated or assigned dynamic level.
    - measure: Measure number in the score.
    - beat: Position of the note within the measure.
    - beatStrength: Relative metrical accent (from weak to strong), calculated for 4/2 time.
"""

from music21 import converter
import csv
import os
import re

# paths config
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(PROJECT_ROOT, "data")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "output")

def run():

    file_path = os.path.join(DATA_PATH, "kyrieII.mxl")

    # Verify that "kyrieII.mxl" exists before proceeding.
    if not os.path.exists(file_path):
        print(f"Error: Could not find file at {file_path}")
        return

    score = converter.parse(file_path)

    # Defining parts (voices)
    choir_parts = ["Soprano I.II.", "Alto.", "Tenore.", "Basso."]

    def safe_filename(name):
        return re.sub(r'[^a-zA-Z0-9]+', '', name).strip().lower()

    for part in score.parts:
        part_name = part.partName

        if part_name not in choir_parts:
            continue

        rows = []

        # Joins the tied notes in order to have a single continuous visual event 
        merged_part = part.stripTies()

        for n in merged_part.recurse().notesAndRests:
            duration = float(n.quarterLength)

            measure_obj = n.getContextByClass("Measure")

            start = float(n.offset)          # local start inside the measure
            end = start + duration           # local end inside the measure

            measure_offset = float(measure_obj.offset) if measure_obj is not None else 0.0

            global_start = measure_offset + start
            global_end = global_start + duration


            measure = n.measureNumber

            try:
                beat = float(n.beat)
            except:
                beat = None

            # Beat strength calculation
            # One 4/2 measure lasts 8 quarter lengths.
            local_pos = start
            
            if local_pos == 0.0:
                beatStrength = 1.0     # 1st half-note (strong downbeat)
            elif local_pos == 4.0:
                beatStrength = 0.5     # 3rd half-note (half-strong)
            elif local_pos in [2.0, 6.0]:
                beatStrength = 0.25    # 2nd e 4th half-note (weak)
            elif local_pos % 1.0 == 0.0:
                beatStrength = 0.125   # quarter note (very weak)
            else:
                beatStrength = 0.0625  # eighth and lower subdivisions

            if n.isRest:
                pitch_midi = None
                pitch_name = "Rest"
                velocity = None
                velocity_realized = None
                
            elif n.isNote:
                pitch_midi = n.pitch.midi
                pitch_name = n.pitch.nameWithOctave
                velocity = None
                velocity_realized = None

                if n.volume is not None:
                    velocity = n.volume.velocity
                    velocity_realized = n.volume.realized

                if velocity is None and velocity_realized is not None:
                    velocity = round(velocity_realized * 127)
                    
            elif n.isChord:
                # In the case of chords (XML artifacts) we keep only the higher note
                top_pitch = n.pitches[-1]
                pitch_midi = top_pitch.midi
                pitch_name = top_pitch.nameWithOctave
                velocity = None
                velocity_realized = None

                if n.volume is not None:
                    velocity = n.volume.velocity
                    velocity_realized = n.volume.realized

                if velocity is None and velocity_realized is not None:
                    velocity = round(velocity_realized * 127)

            # note_id = f"{safe_filename(part_name)}_{start}_{end}_{measure}" 

            note_id = f"{safe_filename(part_name)}_{global_start}_{global_end}_{measure}"

            rows.append([
                note_id,
                part_name,
                start,
                end,
                global_start,
                global_end,
                duration,
                pitch_midi,
                pitch_name,
                velocity_realized,
                velocity,
                measure,
                beat,
                beatStrength
            ])

        filename = os.path.join(OUTPUT_PATH, f"{safe_filename(part_name)}_data.csv")

        print(f"Saving {filename} ({len(rows)} rows)")

        # Creates the output directory if it doesn't exist
        os.makedirs(OUTPUT_PATH, exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
            "note_id",
            "part",
            "start",
            "end",
            "global_start",
            "global_end",
            "duration",
            "pitch_midi",
            "pitch_name",
            "velocity_realized",
            "velocity",
            "measure",
            "beat",
            "beatStrength"
        ])
            writer.writerows(rows)

    print("CSV files generated for all the voices.")

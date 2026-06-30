import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CODE_PATH = os.path.join(PROJECT_ROOT, "code")

sys.path.append(CODE_PATH)

import notes_data_extraction as notes
import harmonic_consonance_extraction as harmonic
import musical_analysis as analysis
import melodic_consonance_extraction as melodic_consonance

def main():
    print("=== START PIPELINE ===")

    print("\n[1/4] SINGLE NOTES DATA EXTRACTION")
    notes.run()

    print("\n[2/4] HARMONIC CONSONANCE EXTRACTION")
    harmonic.run()

    print("\n[3/4] MUSICAL ANALYIS IN PROGRESS")
    analysis.run()

    print("\n[4/4] MELODIC CONSONANCE EXTRACTION")
    melodic_consonance.run()

    print("\n=== PIPELINE COMPLETED ===")

if __name__ == "__main__":
    main()

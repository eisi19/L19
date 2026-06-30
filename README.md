# Project: L19
## Seeing the Unheard: Visualizing the Architecture of Bach’s Mass in B minor

### Description
This repository contains the Python scripts and the TouchDesigner project developed for the music visualization system of **J. S. Bach's _Kyrie II_** from the *Mass in B minor*.

The Python pipeline extracts symbolic musical information from a MusicXML score, including note-level features, contrapuntal structures, and annotated musical-rhetorical figures. It also performs temporal alignment between a reference score audio and a live choir recording using chroma features and Dynamic Time Warping (DTW), producing the data required for synchronized playback.

The extracted data are imported into TouchDesigner, where they drive a real-time generative visualization. Musical elements such as melodic lines, subject entries, harmonic tension, and formal sections are translated into animated curves, moving objects, color variations, and visual effects, creating an audiovisual representation aimed at improving the accessibility of complex polyphonic music.

### How to use the code?

In the corresponding directories there are already the csv files that drive the TouchDesigner project, but if a new generation of them is needed, follow the instructions below.

#### Musical analysis data extraction
Run the **data_extraction.py** script in the directory *musical data extraction*. To run correctly:
- **kyrieII.mxl** has to be in the path *musical data extraction/data*
- **harmonic_consonance_extraction.py**, **melodic_consonance_extraction.py**, **musical_analysis.py**, **notes_data_extraction.py** have to be in the path **musical data extraction/code*

#### Timewarp
Run the **timewarp.py** script in the directory *timewarp*. 
Tu run correctly make sure you have the **musescore.wav** and **coro.wav** files in the same directory of the script.


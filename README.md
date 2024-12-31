# Introduction
The goal of this project is to install a hyperspectral camera in the Laser Diode Floating Zone (LDFZ) furnace at PARADIM Johns Hopkins. Temperature of the melt zone is a critical parameter in floating zone bulk crystal growths, but pyrometry is challenging due to the inability to access the growth for safety reasons and varying emissivity of materials. To overcome these challenges, I have developed a hyperspectral pyrometry method which can determine both temperature and emissivity from a hyperspectral image of the growth. The project also includes physically installing the camera and building the pipeline for streaming, analyzing, and storing images. 

# Repository Structure
## Documents
This folder contains documents for explaining and presenting my work. Most relevant are the pdf files explaining my pyrometry analysis approach and code, the physical setup of the camera and motor, and the design of the data pipeline. There are also json and yml files containing the conda environment that I used for this work.

## PyrometryAnalysis
This folder contains my work and code developing a hyperspectral pyrometry method. There are multiple notebooks containing a variety of data processing and analysis for two images of heated graphite rods. The images are not included in the repository due to their size. There is also code from https://github.com/pytaunay/multiwavelength-pyrometry/tree/master, which I tested but ultimately did not use in the final analysis method. The final method is explained in 'Documents/hyperspectral-analysis.pdf'. **Below is an overview of each of the files in chronological order of the development of the analysis.**

'SpectralPy-practice.ipynb' - this notebook was for testing the SpectralPy package for importing and manipulating hyperspectral image data. It does not contain any analysis.

'graphite-rod.ipynb' - this notebook contains initial pyrometry analysis using the first graphite rod image. This is the starting point of the pyrometry analysis work.

'graphite-rod-averagingframes.ipynb' - this notebook repeats the pyrometry analysis of 'graphite-rod.ipynb' but averages varying numbers of frames over time in an attempt to reduce the impact of noise in the image.

'graphite-rod-offset.ipynb' - this notebook repeats the previous pyrometry analysis but adds a constant offset parameter to the blackbody equation for fitting. With this correction, a full analysis of a single point on the rod is performed to see the change in temperature over time. 

'graphite_rod_2.ipynb' - this notebook repeats all of the previous pyrometry techniques using a better graphite rod image with less background light. 

'graphite_rod_2_other_ideas.ipynb' - this notebook uses various other techniques including removing high noise data at lower wavelengths and not initially correcting data to get the best pyrometry analysis. This has the best results and is used in the scripts.

'clean_analysis.py' - this script stores the most successful pyrometry analysis from 'graphite_rod_2_other_ideas.ipynb' without the extra attempts and testing.

'vectorizing-pyrometry.ipynb' - this notebook contains a first attempt to further vectorize the pyrometry analysis to improve efficiency. It also contains comparison to the final analysis developed previously and runtime comparisons.

## MotorControl
This folder contains an Arduino sketch and relevant information for its dependencies and setup. The sketch programs the Raspberry Pi to respond to the camera's Hyperspec III software and move the camera down and up repeatedly for some set number of motor ticks, which can be adjusted in the sketch. The physical setup and sketch are explained in 'Documents/hyperspectral-LDFZ-motor.pdf'

## StreamingScripts
This folder contains the scripts I use for the final data streaming and analysis. They are explained in 'Documents/hyperspectral-LDFZ-pipeline.pdf'. There are also Dockerfiles used for containerizing the stream processor.

## StreamProcessorContainer
This folder contains the files used to containerize the stream processor and run it on the paradim01 server.

## ProjectFinalResults
This folder contains hyperspectral images from the LDFZ and analysis and processing of the images to generate results for my project final presentation.

## OldFiles
This folder contains notebooks I used for learning and testing data streaming and are **not needed**.

# Most Recent Versions
The most recent working version of the analysis can be found in 'StreamingScripts/' and is identical to the version in 'StreamProcessorContainer/'. This is based on the most successful version in 'PyrometryAnalysis/graphite_rod_2_other_ideas.ipynb'. An attempt to vectorize the code is found in 'PyrometryAnalysis/vectorizing-pyrometry.ipynb'. This is not complete as it gives temperatures that are slightly inconsistent with the version in 'StreamingScripts/'. 

# Introduction
The goal of this project is to install a hyperspectral camera in the Laser Diode Floating Zone (LDFZ) furnace at PARADIM Johns Hopkins. Temperature of the melt zone is a critical parameter in floating zone bulk crystal growths, but pyrometry is challenging due to the inability to access the growth for safety reasons and varying emissivity of materials. To overcome these challenges, I have developed a hyperspectral pyrometry method which can determine both temperature and emissivity from a hyperspectral image of the growth. The project also includes physically installing the camera and building the pipeline for streaming, analyzing, and storing images. 

# Repository Structure
## Documents
This folder contains documents for explaining and presenting my work. Most relevant are the pdf files explaining my pyrometry analysis approach and code, the physical setup of the camera and motor, and the design of the data pipeline. There are also json and yml files containing the conda environment that I used for this work.

## PyrometryAnalysis
This folder contains my work and code developing a hyperspectral pyrometry method. There are multiple notebooks containing a variety of data processing and analysis for two images of heated graphite rods. The images are not included in the repository due to their size. There is also code from https://github.com/pytaunay/multiwavelength-pyrometry/tree/master, which I tested but ultimately did not use in the final analysis method. The final method is explained in 'Documents/hyperspectral-analysis.pdf'.

## MotorControl
This folder contains an Arduino sketch and relevant information for its dependencies and setup. The sketch programs the Raspberry Pi to respond to the camera's Hyperspec III software and move the camera down and up repeatedly for some set number of motor ticks, which can be adjusted in the sketch. The physical setup and sketch are explained in 'Documents/hyperspectral-LDFZ-motor.pdf'

## StreamingScripts
This folder contains the scripts I use for the final data streaming and analysis. They are explained in 'Documents/hyperspectral-LDFZ-pipeline.pdf'. There are also Dockerfiles used for containerizing the stream processor.

## StreamProcessorContainer
This folder contains the files used to containerize the stream processor and run it on the paradim01 server.

## OldFiles
This folder contains notebooks I used for learning and testing data streaming and are **not needed**.

FROM continuumio/miniconda3
WORKDIR /Users/namanparikh/Documents/GitHub/paradim/reu2024-hyperspectral-camera/StreamingScripts

# Create the environment:
# COPY env.yml ./
# RUN conda env create -f env.yml

# Create the environment:
RUN conda create -n hyperspec_ldfz_analysis python=3.9

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "hyperspec_ldfz_analysis", "/bin/bash", "-c"]

# Install needed packages:
RUN conda install -c anaconda libsodium
RUN pip install openmsistream
RUN conda install numpy scipy matplotlib
RUN pip install spectral
RUN pip install tqdm

# The code to run when container is started:
COPY processor.py ./
COPY temperature_analysis.py ./
COPY config_files/paradim01_broker.config ./
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "hyperspec_ldfz_analysis", "python", "processor.py"]
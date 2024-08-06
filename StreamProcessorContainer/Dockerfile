FROM continuumio/miniconda3:4.12.0
LABEL Build docker build --rm --tag paradim/hyperspec_analysis --format docker .
LABEL Run docker run -d --mount type=bind,source=/config-dir,target=/hyspec/config,rw --mount type=bind,source=/large_data_storage_location,target=/hyspec/hyperspec_LDFZ_data,rw paradim/hyperspec_analysis

RUN mkdir /hyspec && \
    mkdir /hyspec/config && \
    mkdir /hyspec/hyperspec_LDFZ_data

WORKDIR /hyspec

RUN ln -s ./config/paradim01_broker.config ./paradim01_broker.config

# Create the environment:
RUN conda create -n hyperspec_ldfz_analysis -y python=3.9

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "hyperspec_ldfz_analysis", "/bin/bash", "-c"]

# Install needed packages:
RUN conda install -y -c anaconda libsodium
RUN pip install openmsistream
RUN conda install -y numpy scipy matplotlib
RUN pip install spectral
RUN pip install tqdm

# The code to run when container is started:
COPY processor.py ./
COPY temperature_analysis.py ./
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "hyperspec_ldfz_analysis", "python", "processor.py"]


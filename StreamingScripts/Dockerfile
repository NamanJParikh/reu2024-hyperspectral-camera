FROM continuumio/miniconda3
WORKDIR /home/nparik15

# Create the environment:
COPY env.yml ./
RUN conda env create -f env.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "openmsi", "/bin/bash", "-c"]

# The code to run when container is started:
COPY processor.py ./
COPY temperature_analysis.py ./
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "openmsi", "python", "processor.py"]
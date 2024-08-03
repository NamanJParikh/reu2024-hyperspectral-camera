# FROM python:3.9
# WORKDIR /home/nparik15

# COPY env.yml ./
# RUN conda env create -f env.yml

# COPY processor.py ./

# CMD ["python", "processor.py"]

FROM continuumio/miniconda3

WORKDIR /home/nparik15

# Create the environment:
COPY env.yml ./
RUN conda env create -f env.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "openmsi", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# The code to run when container is started:
COPY processor.py ./
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "openmsi", "python", "processor.py"]
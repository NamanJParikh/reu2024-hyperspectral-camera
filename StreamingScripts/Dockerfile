FROM python:3.9
WORKDIR /home/nparik15

COPY env.yml ./
RUN conda env create -f env.yml

COPY processor.py ./

CMD ["python", "processor.py"]
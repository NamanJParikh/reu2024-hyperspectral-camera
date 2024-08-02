FROM python:3.9
WORKDIR /home/nparik15

COPY environment.yml ./
RUN conda create -f environment.yml

ADD processor.py

RUN useradd app
USER app

CMD ["python", "processor.py"]
FROM continuumio/miniconda3

WORKDIR /home/app

RUN apt-get update

COPY requirements.txt /dependencies/requirements.txt
RUN pip install -r /dependencies/requirements.txt

COPY . /home/app

CMD streamlit run --server.port $PORT app.py
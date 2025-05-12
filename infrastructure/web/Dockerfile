FROM python:3.10.16
WORKDIR /code
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8501
COPY . /code
CMD streamlit run --server.port 8501 app.py
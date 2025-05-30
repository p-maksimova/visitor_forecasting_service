FROM python:3.10.16
WORKDIR /code
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . /code
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
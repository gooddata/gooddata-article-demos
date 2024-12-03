# Use an official Python runtime as a parent image
FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3"]
#CMD ["tail" ,"-f", "/dev/null"]
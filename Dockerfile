FROM python:3.6-stretch
RUN apt update
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
ADD . /app
ENV PORT 8080
CMD ["gunicorn", "flask_api:app", "--config=gunicorn_config.py"]

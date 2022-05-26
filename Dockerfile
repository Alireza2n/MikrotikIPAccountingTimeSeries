FROM python:3.10

COPY requirements.txt /opt/app/

RUN pip install pip -U
RUN pip install -r /opt/app/requirements.txt

COPY ./src /opt/app

ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "/opt/app/main.py"]
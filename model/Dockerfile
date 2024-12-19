FROM umihico/aws-lambda-selenium-python:latest

# copy all python files and modules
COPY db /var/task/db
COPY fetch /var/task/fetch
COPY league /var/task/league
COPY players /var/task/players
COPY process /var/task/process
COPY config.py /var/task/config.py
COPY handler.py /var/task/handler.py
COPY requirements.txt /var/task/requirements.txt

RUN pip install -r /var/task/requirements.txt

CMD [ "handler.handler" ]
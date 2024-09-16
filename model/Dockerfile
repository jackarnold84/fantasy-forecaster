FROM umihico/aws-lambda-selenium-python:latest

COPY ./ ./

RUN pip install -r requirements.txt

CMD [ "handler.handler" ]
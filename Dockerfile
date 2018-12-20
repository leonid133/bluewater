FROM python:2.7

WORKDIR /source

ENV FLASK_APP app.py

EXPOSE 5000

ADD ./src /source

RUN pip install -r requirements.txt

#CMD ["python", "app.py", "--host=0.0.0.0"]
CMD ["flask", "run", "--host=0.0.0.0"]

FROM python:3.6-alpine
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 9000
# CMD python3 run.py
CMD gunicorn --reload -b 0.0.0.0:9000 -w 4 run:app
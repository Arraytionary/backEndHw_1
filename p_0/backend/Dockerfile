FROM python:3.6-alpine
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV MONGO_INITDB_DATABASE mango
EXPOSE 5000
CMD gunicorn --reload -b 0.0.0.0:5000 -w 4 app:app

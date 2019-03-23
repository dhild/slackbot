#Grab the latest alpine image
FROM python:3.7-alpine

# Install python and pip
RUN apk add --no-cache --update bash musl-dev linux-headers g++ && pip3 install --upgrade pip

# Install spacy separately because it takes forever:
RUN pip3 install --no-cache-dir spacy>=2.0.18 && python -m spacy download en

# Now install the rest of the dependencies:
ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

# Expose is NOT supported by Heroku
# EXPOSE 5000

# Run the image as a non-root user
RUN adduser -D slackbot
USER slackbot

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD gunicorn --bind 0.0.0.0:$PORT wsgi

#Grab the latest spacey image
FROM quay.io/rhild/spacey-python

# Install pip, build, and runtime dependencies
RUN apk add --no-cache --update bash musl-dev linux-headers g++ postgresql-dev && pip3 install --upgrade pip

# Now install the rest of the dependencies:
ADD ./webapp/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Add our code
ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

# Run the image as a non-root user
RUN adduser -D slackbot
USER slackbot

# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD gunicorn --bind 0.0.0.0:$PORT wsgi

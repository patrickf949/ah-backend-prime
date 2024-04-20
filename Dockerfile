# Use an official Python runtime as a parent image
FROM python:3.8.19

# Set ARGironment variables
ARG SECRET_KEY
ARG DEBUG
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_PORT
ARG EMAIL_PASSWORD
ARG EMAIL
ARG EMAIL_HOST  
ARG SOCIAL_PASSWORD
ARG TWITTER_CONSUMER_API_KEY
ARG TWITTER_CONSUMER_API_SECRET


ENV SECRET_KEY=${SECRET_KEY} DEBUG=${DEBUG} DB_NAME=${DB_NAME} DB_USER=${DB_USER} \
    DB_PASSWORD=${DB_PASSWORD} DB_HOST=${DB_HOST} DB_PORT=${DB_PORT} \
    EMAIL_PASSWORD=${EMAIL_PASSWORD} EMAIL=${EMAIL} EMAIL_HOST=${EMAIL_HOST} \
    SOCIAL_PASSWORD=${SOCIAL_PASSWORD} TWITTER_CONSUMER_API_KEY=${TWITTER_CONSUMER_API_KEY} \
    TWITTER_CONSUMER_API_SECRET=${TWITTER_CONSUMER_API_SECRET}

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        gettext \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the project code into the container
COPY . /app

# Install Python dependencies
# RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port that Django runs on
EXPOSE 8080

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]

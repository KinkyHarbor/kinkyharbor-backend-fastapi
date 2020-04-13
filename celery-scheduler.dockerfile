FROM python:3.8

# Setup ENV
WORKDIR /usr/src/app

# Install dependencies
RUN pip install --no-cache-dir celery fastapi motor email_validator aiofiles

# Create non-root user
RUN useradd celery

# Create volume for data
RUN mkdir /data && chown celery:celery /data
VOLUME ["/data"]

# Copy Harbor into container
COPY --chown=celery:celery . .

# Start scheduler
# Note to self: Check for trailing comma if you get following error:
# /bin/sh: 1: [: celery,: unexpected operator
USER celery
CMD [ "celery", \
      "beat", \
      "--app", "harbor.worker.app", \
      "--schedule", "/data/celerybeat-schedule.db", \
      "--pidfile", "/data/celerybeat.pid", \
      "--loglevel", "info" \
]
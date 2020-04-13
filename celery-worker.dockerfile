FROM python:3.8

# Setup ENV
WORKDIR /usr/src/app

# Install dependencies
RUN pip install --no-cache-dir celery

# Create non-root user
RUN useradd celery
USER celery

# Copy Harbor into container
COPY --chown=celery:celery . .

# Start worker
# Note to self: Check for trailing comma if you get following error:
# /bin/sh: 1: [: celery,: unexpected operator
CMD [ "celery", \
      "worker", \
      "--app", "harbor.worker.app", \
      "--loglevel", "info", \
      "--concurrency", "1" \
]
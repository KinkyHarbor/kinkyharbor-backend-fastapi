FROM python:3.8

# Setup ENV
WORKDIR /usr/src/app

# Install dependencies
RUN pip install --no-cache-dir celery

# Create non-root user
RUN useradd worker
USER worker

# Copy Harbor into container
COPY --chown=worker:worker . .

# Start worker
CMD [ "celery", \
      "worker", \
      "-A", "harbor.worker.app", \
      "-l", "info", \
      "-c", "1" \
]

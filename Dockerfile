FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Setup ENV
ENV MODULE_NAME harbor.app

# Copy Harbor into container
COPY . /app/

# Install dependencies
RUN pip install -r /app/requirements.txt
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Copy Harbor into container
COPY ./app /app/

# Install dependencies
COPY requirements.txt /
RUN pip install -r /requirements.txt
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# Copy Harbor into container
COPY ./app /app/

# Install dependencies
RUN pip install -r /app/requirements.txt
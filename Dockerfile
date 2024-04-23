FROM python:3.11-slim-bullseye

# Set the working directory
WORKDIR /src

# Copy the requirements.txt
COPY requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the files
COPY ./app ./app

ENV PYTHONPATH=/src;/src/app

WORKDIR /src
# Start the app

RUN addgroup --system nonroot \
    && adduser --system nonroot --ingroup nonroot

USER nonroot

CMD uvicorn app.main:app --host 0.0.0.0 --port 8080
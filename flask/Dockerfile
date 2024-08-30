# Use the official Python image from the Debian-based version
FROM python:3.11-slim-buster AS build-stage
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Expose the necessary port
EXPOSE 5005

# Run the application
CMD ["python", "app.py"]

# build command: docker build -t fitbit .
# run command: docker run -p 5000:5000 fitbit
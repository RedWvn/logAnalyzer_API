# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system packages
RUN apt-get update && \
    apt-get install -y libxml2 libxml2-dev libxslt1-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]

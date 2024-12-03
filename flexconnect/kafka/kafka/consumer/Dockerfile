# It is necessary to use slim-bullseye instead of alpine because of pyarrow
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY consume.py .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to keep the container running
CMD ["python3", "consume.py"]

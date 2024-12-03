FROM python:3.12-alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY populate.py .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to keep the container running
CMD ["python3", "populate.py"]

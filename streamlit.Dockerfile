# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project context into the container
COPY . /app

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define a health check
HEALTHCHECK CMD streamlit hello

# Run dashboard/main.py when the container launches
CMD ["streamlit", "run", "dashboard/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

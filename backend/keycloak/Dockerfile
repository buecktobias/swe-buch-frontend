# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port on which the Keycloak API will run (optional, if needed for access)
EXPOSE 8080

# Command to run the Python script
CMD ["python", "./keycloak_manager.py"]

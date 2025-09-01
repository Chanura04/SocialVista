# Use a lightweight official Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port for your Flask application (if needed)
EXPOSE 5000

# The CMD will be overridden by docker-compose for each service
CMD ["python", "app.py"]
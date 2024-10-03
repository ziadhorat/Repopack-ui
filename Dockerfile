# Use Alpine Linux as the base image
FROM python:3.11-alpine

# Install necessary build dependencies
RUN apk add --no-cache nodejs npm git

# Install repopack globally
RUN npm install -g repopack

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Copy the config file
COPY repopack.config.json /app/repopack.config.json

# The port to expose
EXPOSE 32123

# Run the application
CMD ["python", "app.py"]
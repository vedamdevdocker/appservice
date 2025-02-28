# Use official Python image with version 3.10 or later
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY app/requirements.txt ./

# Upgrade pip to ensure the latest version
RUN python -m pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files, excluding unnecessary folders via .dockerignore
COPY app/ ./

# Copy SSL certificates into the container
COPY certs/appservice/server.crt /etc/ssl/certs/appservice.crt
COPY certs/appservice/server.key /etc/ssl/private/appservice.key

# Expose HTTPS port
EXPOSE 5223

# Start Gunicorn with HTTPS
CMD ["gunicorn", "-b", "0.0.0.0:5223", "--certfile=/etc/ssl/certs/appservice.crt", "--keyfile=/etc/ssl/private/appservice.key", "app:app"]

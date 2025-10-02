# Use slim Python 3.11 base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements and install dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app into the container
COPY . /app

# Expose the port your app will run on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=python_login_webapp/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV ENV=production

# Run the Flask app
CMD ["flask", "run"]

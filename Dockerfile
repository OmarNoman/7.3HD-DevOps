# Using python 3.11 for image
FROM python:3.11-slim

# Sets up the working directory
WORKDIR /app

# Copies the requirements file and instals the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copies the rest of the app into the contianer
COPY . /app

# Exposes the port for the app to run on
EXPOSE 5000

# Sets the environment variables
ENV FLASK_APP=python_login_webapp/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV ENV=production

# Runs the flask program
CMD ["flask", "run"]

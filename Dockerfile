# Use the official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements (if you have one)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the program
CMD ["python", "python_login.py"]

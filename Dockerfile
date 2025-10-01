FROM python:3.11-slim

WORKDIR /app
COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Default env vars for CI/CD
ENV CI=true
ENV USERNAME=test
ENV PASSWORD=123

COPY . .

# Run the program
CMD ["python", "python_login.py"]

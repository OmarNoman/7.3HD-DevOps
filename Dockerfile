FROM python:3.11-slim

WORKDIR /app
COPY . /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install bandit

# Default env vars for CI/CD
ENV CI=true
ENV USERNAME=omar
ENV PASSWORD=123

COPY . .

# Run the program
CMD ["python", "python_login.py"]

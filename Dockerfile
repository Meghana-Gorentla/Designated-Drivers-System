# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory in container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full app source code
COPY . .

# Ensure Python can find your app folder
ENV PYTHONPATH=/app

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

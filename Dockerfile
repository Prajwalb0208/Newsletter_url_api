# Use official python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose default port (Railway sets $PORT, so this is for convention)
EXPOSE 8000

# Startup command using Railway-injected $PORT variable
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

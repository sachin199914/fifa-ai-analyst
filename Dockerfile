FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the entire project (backend and data folders are needed)
COPY . .

# Change to backend directory
WORKDIR /app/backend

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Hugging Face Spaces exposes port 7860 by default
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

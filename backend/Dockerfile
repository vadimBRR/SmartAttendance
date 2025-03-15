FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set timezone (change to your desired timezone, e.g., Europe/Bratislava)
ENV TZ=Europe/Bratislava

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . .

# Ensure the target directory exists in the container
RUN mkdir -p /app/src/database

# Copy the database file from the build context
COPY src/database/uni_attendance.db /app/src/database/uni_attendance.db

# Expose the application port
EXPOSE 80

# Start the application with uvicorn and ensure scheduler runs
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

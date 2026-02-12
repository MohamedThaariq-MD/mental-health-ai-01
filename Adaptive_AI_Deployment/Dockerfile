# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for OpenCV and AI libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt ./backend/

# Install any needed packages specified in requirements.txt
# Note: Using tensorflow-cpu for smaller image size and compatibility
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && pip install --no-cache-dir tensorflow-cpu==2.15.0

# Copy the rest of the application code
COPY . .

# Expose ports for Flask (5000) and Streamlit (8501)
EXPOSE 5000 8501

# Create a startup script to run both services
RUN echo '#!/bin/bash\n\
python backend/app.py & \n\
streamlit run ui/dashboard.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]

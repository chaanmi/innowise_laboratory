# Step 1: Use the official lightweight Python base image
# This provides a minimal Debian-based environment with Python 3.11 pre-installed
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
# All subsequent commands will be executed relative to this path
WORKDIR /app

# Step 3: Copy dependency file (if exists). Commented out as we don't have one yet.
# This is the standard pattern for multi-stage builds to leverage Docker cache
# COPY requirements.txt .

# Step 4: Install Python dependencies (if any). Skipping for now.
# Using --no-cache-dir reduces image size by not storing pip cache
# RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy application source code into the container
# The dot (.) refers to current directory in build context (WORKDIR /app)
COPY main.py .

# Step 6: Install FastAPI framework and Uvicorn ASGI server
# These packages are required to run the FastAPI application
RUN pip install --no-cache-dir fastapi uvicorn

# Step 7: Document the network port this container will listen on
# This is informational only; actual port mapping happens at runtime with -p flag
EXPOSE 8000

# Step 8: Default command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# 1. Base Image
# Use a lightweight, stable Python base image.
FROM python:3.11-slim

# 2. Environment Setup
# Prevents Python from writing .pyc files (faster build)
ENV PYTHONDONTWRITEBYTECODE 1
# Forces stdout and stderr streams to be unbuffered (better logging in container)
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory
WORKDIR /app

# 4. Install System Dependencies
# 'libpq-dev' is required for the 'psycopg2' package to compile and connect to Postgres.
# 'gcc' is often needed to compile Python packages with C extensions.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# 5. Copy Requirements and Install Python Dependencies
# Copying this first allows Docker to cache this layer, speeding up subsequent builds
# unless requirements.txt changes.
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 6. Copy Application Code
# Copy the rest of the application source code into the container
COPY . /app/



# 8. Expose Port
# Tell Docker which port the container will listen on. Gunicorn usually defaults to 8000.
EXPOSE 8000

# 9. Startup Command
# Run the application using Gunicorn, binding it to 0.0.0.0 on port 8000.
# IMPORTANT: Replace 'your_project_name.wsgi' with the actual path to your WSGI file (e.g., 'myproject.wsgi').
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "cropdoc.wsgi"]

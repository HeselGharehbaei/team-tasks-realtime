# Base image
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the entire project
COPY . /app

# Expose port for Django/Daphne
EXPOSE 8000

# Default command (برای توسعه سریع)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

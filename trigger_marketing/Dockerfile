# Use Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install backend and celery dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire code into the container
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Default CMD will be overridden by docker-compose for Celery or backend
CMD ["sh", "-c", "gunicorn trigger_marketing.wsgi:application --bind 0.0.0.0:8000"]

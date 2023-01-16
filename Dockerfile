FROM alpine:3.17.1

# Create and set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN apk update \
    && apk add python3 python3-dev py3-pip libffi-dev build-base nodejs npm \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && npm install

# Run TailwindCSS
RUN npx tailwindcss -i ./input.css -o ./static/css/styles.css --minify

# Expose the port 8000
EXPOSE 8000

# Start Gunicorn
# Default worker nodes is 2 for a 1-core VM, set to number of cores + 1
CMD python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn main.wsgi --bind 0.0.0.0:8000 --workers 2 --worker-tmp-dir /dev/shm --log-file=-
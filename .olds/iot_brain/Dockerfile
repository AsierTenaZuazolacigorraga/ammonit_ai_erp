FROM python:3.10

# Set environment variables
ENV PYTHONPATH="/workdir/"

# Copy and et work directory
WORKDIR /workdir
COPY subscriber /workdir/subscriber
COPY commons_py /workdir/commons_py
COPY requirements.txt /workdir/requirements.txt
COPY .env /workdir/.env

# Install necessary things
RUN pip install --no-cache-dir -r requirements.txt

# Execute command
# To test setup before CMD -> CMD ["python", "-c", "import time; time.sleep(1000000)"]
CMD ["python", "subscriber/src/__main__.py"]
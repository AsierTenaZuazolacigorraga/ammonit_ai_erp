FROM python:3.10

# Set environment variables
ENV PYTHONPATH="/workdir/"

# Copy and et work directory
WORKDIR /workdir
COPY backend /workdir/backend
COPY commons_py /workdir/commons_py
COPY requirements.txt /workdir/requirements.txt
COPY .env /workdir/.env

# Install necessary things
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Execute command
# To test setup before CMD -> CMD ["python", "-c", "import time; time.sleep(1000000)"]
CMD ["uvicorn", "src.__main__:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
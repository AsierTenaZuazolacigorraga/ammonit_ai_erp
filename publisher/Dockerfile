FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/workdir/app"

# Copy and et work directory
WORKDIR /workdir
COPY . /workdir

# Install necessary things
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8501

# Execute command
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
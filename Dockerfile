# Use the official Python image as the base
FROM python:3.11-slim

# Set environment variables to prevent Python from buffering stdout/stderr
# ENV PYTHONUNBUFFERED=1 \
#     PIP_NO_CACHE_DIR=1 \
#     STREAMLIT_HOME="/app"

# Set the working directory in the container
WORKDIR /app

# Copy the entire Streamlit app into the container
COPY . .

# # Copy requirements.txt first to leverage Docker cache
# COPY requirements.txt .
# COPY Layout.py .
# COPY frost_server.py .
# COPY app.py .
# COPY vis.py .


# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "Layout.py", "--server.port=8501", "--server.address=localhost"]

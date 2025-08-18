# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python libs like PyPDF)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port Streamlit will run on (Render maps $PORT)
EXPOSE 10000

# Streamlit requires some config tweaks for Docker/Render
ENV STREAMLIT_SERVER_PORT=10000 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_BASE=dark
    

# Start Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port", "10000", "--server.address", "0.0.0.0"]

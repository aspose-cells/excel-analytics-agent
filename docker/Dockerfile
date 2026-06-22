FROM python:3.11-slim

WORKDIR /app

# =========================
# System dependencies
# =========================
RUN apt-get update && apt-get install -y \
    wget \
    libgdiplus \
    && rm -rf /var/lib/apt/lists/*

# =========================
# ICU installation
# =========================
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/i/icu/libicu70_70.1-2_amd64.deb \
    && dpkg -i libicu70_70.1-2_amd64.deb || apt-get install -f -y \
    && rm libicu70_70.1-2_amd64.deb

# =========================
# Python deps
# =========================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# App code
# =========================
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]

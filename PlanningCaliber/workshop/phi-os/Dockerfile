# PHI-OS v1.0.0 — Proof of Reproducibility
# Python + Node.js + Chromium (Chrome拡張E2E対応)

FROM node:20-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    chromium \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

WORKDIR /phios

COPY test/package*.json test/
RUN cd test && npm install --no-audit --no-fund

COPY . .

CMD ["python3", "-X", "utf8", "reproduce_phios.py"]

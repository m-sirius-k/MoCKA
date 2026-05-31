# PHI-OS (Relay v4.1.0) — Proof of Reproducibility
# Python + Node.js + Chromium (Chrome拡張E2E対応)

FROM node:20-bookworm-slim

# ─── システム依存パッケージ ────────────────────────────────────────────────────
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
    libgconf-2-4 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# ─── Puppeteer: システムChromiumを使用（独自ダウンロード不要）──────────────────
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUTF8=1

WORKDIR /phios

# ─── Node.js依存パッケージ（Puppeteer）────────────────────────────────────────
COPY test/package*.json test/
RUN cd test && npm install --no-audit --no-fund

# ─── プロジェクト全体をコピー ─────────────────────────────────────────────────
COPY . .

CMD ["python3", "-X", "utf8", "reproduce_phios.py"]

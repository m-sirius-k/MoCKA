FROM python:3.12-slim

WORKDIR /vasai

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV VASAI_HMAC_KEY=docker-reproduce-key
ENV PYTHONIOENCODING=utf-8

EXPOSE 6000

CMD ["python", "reproduce_l48.py"]

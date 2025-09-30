FROM python:3.12-slim

WORKDIR /app

# Install poppler-utils for PDF support
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr libgl1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt

COPY . .

# Render sets $PORT; default to 8000 for local runs
# Prefer CMD so Render can override if needed
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000" ]
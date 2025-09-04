FROM python:3.12

WORKDIR /app

# Install poppler-utils for PDF support
RUN apt-get update && apt-get install -y poppler-utils tesseract-ocr

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
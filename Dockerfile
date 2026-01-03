FROM python:3.12-slim

WORKDIR /app

# system deps (optional but helps common libs)
RUN pip install --no-cache-dir --upgrade pip

# Copy and install deps first (better caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . /app

# Render/Railway often sets PORT, but locally we'll use 8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
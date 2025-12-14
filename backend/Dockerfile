# Gunakan Python 3.10 sesuai environment Anda
FROM python:3.10-slim

WORKDIR /app

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh isi folder backend ke container
COPY . .

# Jalankan aplikasi
CMD ["python", "app.py"]
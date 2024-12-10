FROM python:3.9-slim

# تحديد العمل داخل المجلد /app
WORKDIR /app

# نسخ الملفات المطلوبة
COPY . .

# تثبيت الحزم
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["python", "app.py"]

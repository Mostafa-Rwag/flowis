# نبدأ من صورة Python الرسمية
FROM python:3.9-slim

# تثبيت الحزم الأساسية التي تشمل libGL
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# إعداد المجلد داخل الحاوية
WORKDIR /app

# نسخ المتطلبات وتثبيتها
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# نسخ جميع الملفات الأخرى إلى الحاوية
COPY . /app/

# تعيين المنفذ 8080 ليتم تشغيل التطبيق عليه
EXPOSE 8080

# تشغيل التطبيق
CMD ["python", "app.py"]

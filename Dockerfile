FROM python:3.9

# تثبيت مكتبة libGL المطلوبة
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# نسخ ملف المتطلبات وتثبيت الحزم
COPY requirements.txt .
RUN pip install -r requirements.txt

# نسخ التطبيق
COPY . /app
WORKDIR /app

# تشغيل التطبيق
CMD ["python", "app.py"]

# استخدام نسخة بايثون 3.11 الخفيفة والمتوافقة مع الخادم
FROM python:3.11-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات أولاً وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي أكواد المشروع
COPY src/ ./src/
COPY .github/ ./.github/

# ضبط إعدادات البيئة
ENV PYTHONPATH=/app
EXPOSE 8000

# الأمر الافتراضي لتشغيل الخدمة
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
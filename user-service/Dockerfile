FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5001

CMD ["sh", "-c", "python -c 'from app import app, db; app.app_context().push(); db.create_all()' && exec gunicorn --bind 0.0.0.0:5001 --workers 2 app:app"]

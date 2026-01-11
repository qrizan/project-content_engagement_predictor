FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy file app
COPY app.py .
COPY model/ model/
COPY templates/ templates/
COPY static/ static/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
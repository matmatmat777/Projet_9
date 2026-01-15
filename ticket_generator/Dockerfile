FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ticket_generator.py .

CMD ["python", "ticket_generator.py"]

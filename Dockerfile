FROM python:3.8

ADD requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /app
ADD src /app

WORKDIR /app

# CMD ["gunicorn", "main:app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0", "--log-level", "info"]
CMD ["python", "/app/main.py"]

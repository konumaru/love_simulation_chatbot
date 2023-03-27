ARG PYTHON_VERSION="python3.10"
FROM tiangolo/uvicorn-gunicorn-fastapi:${PYTHON_VERSION}

ENV PYTHONUNBUFFERED True

COPY ./app /app/
COPY requirements.txt requirements.txt

RUN pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
CMD ["uvicorn", "main:app", "--reload","--host", "0.0.0.0", "--port", "8080"]

ARG PYTHON_VERSION="python3.10"

FROM tiangolo/uvicorn-gunicorn-fastapi:${PYTHON_VERSION}

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false 

ARG DEV=false
RUN if [ "$DEV" = "true" ] ; then poetry install --with dev ; else poetry install --only main ; fi

COPY ./app/ ./
COPY ./data/ ./data/
COPY ./prompts/ ./prompts/

EXPOSE $PORT
CMD python main.py

FROM python:3.10.13-alpine
WORKDIR /app
COPY ./src/requirements.txt .
RUN pip install -r requirements.txt
COPY ./src .
CMD gunicorn -w 3 -b 0.0.0.0:8000 main:app
EXPOSE 8000
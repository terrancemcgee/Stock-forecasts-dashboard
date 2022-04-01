
FROM python:3.9-slim-buster

WORKDIR /app
EXPOSE 8080

.
RUN pip install -r requirements.txt

COPY ./app





CMD streamlit run --server.port 8080 --server.enableCORS false app.py


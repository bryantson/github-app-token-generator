FROM ghcr.io/bryantson/python:3.9.15-slim

COPY generate-jwt.py generate-jwt.py

RUN pip install --no-cache-dir pyjwt requests cryptography

ENTRYPOINT ["python3","/generate-jwt.py"]
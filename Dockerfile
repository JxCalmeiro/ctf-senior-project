FROM python:3.12-slim

WORKDIR /app

COPY ctf-root-ca.crt /usr/local/share/ca-certificates/ctf-root-ca.crt
RUN update-ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]

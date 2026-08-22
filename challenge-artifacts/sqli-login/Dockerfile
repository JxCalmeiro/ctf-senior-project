FROM python:3.12-slim
WORKDIR /app
RUN pip install flask
COPY vuln_app.py .
EXPOSE 5001
CMD ["python", "vuln_app.py"]

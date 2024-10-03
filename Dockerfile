FROM python:3.11-slim
RUN apt-get update && apt-get install -y nodejs npm && npm install -g repopack
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY repopack.config.json /app/repopack.config.json
EXPOSE 32123
CMD ["python", "app.py"]

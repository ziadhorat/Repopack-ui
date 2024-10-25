# 📦 Repopack-ui 
This aims to be a simple & small application that's a containerised web gui for [yamadashy/repopack](https://github.com/yamadashy/repopack).

Repopack is a powerful tool that packs your entire repository into a single, AI-friendly file.


![size](https://img.shields.io/docker/image-size/ziadhorat/repopack-ui/latest?color=0eb305)
![pulls](https://img.shields.io/docker/pulls/ziadhorat/repopack-ui?color=2b75d6) 
[![GitHub Release][release-img]][release]
[![License][license-img]][license]
[![CodeQL](https://github.com/ziadhorat/Repopack-ui/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/ziadhorat/Eepopack-ui/actions/workflows/github-code-scanning/codeql)
[![Trivy](https://github.com/ziadhorat/Repopack-ui/actions/workflows/trivy.yml/badge.svg)](https://github.com/ziadhorat/Repopack-ui/actions/workflows/trivy.yml)
[![Docker Image CI](https://github.com/ziadhorat/Repopack-ui/actions/workflows/docker-image.yml/badge.svg)](https://github.com/ziadhorat/Repopack-ui/actions/workflows/docker-image.yml)

[Dockerhub - ziadhorat/repopack-ui](https://hub.docker.com/r/ziadhorat/repopack-ui)

![Screenshot](https://github.com/user-attachments/assets/5a4f4268-ce43-4592-8f6a-54c15d1921e4)


## 🚀 Docker Run Command
If you prefer to run the container using `docker run`, use the following command:
```bash
docker run -d --name repopack-ui \
  -p 32123:32123 \
  ziadhorat/repopack-ui
```
Open a web browser and navigate to `http://container-ip:32123`.

## 📊 Deploy with docker compose

Create a `docker-compose.yml`:
```yaml
version: '3'
services:
  repopack-ui:
    container_name: repopack-ui
    image: ziadhorat/repopack-ui
    ports:
      - "32123:32123"
```
Run `docker compose up -d`.

Open a web browser and navigate to `http://container-ip:32123`.

## 📌 Local development (docker compose)

### 1. Clone the repository
```bash
git clone https://github.com/ziadhorat/Repopack-ui.git
cd repopack-ui/development
```

### 2. Build and run using Docker Compose
```bash
docker-compose up --build
```
### 3. Access the app
Open a web browser and navigate to `http://localhost:32123`.

## 📝 TODO
- Make radio buttons inline aswell
- Check if config works
- Fix the 2 check boxes that dont work
  
## ✨ Contributing
Feel free to submit issues, feature or pull requests. 
All contributions are welcome!

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

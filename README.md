# Repopack-ui 

[Dockerhub - ziadhorat/repopack-ui](https://hub.docker.com/r/ziadhorat/repopack-ui)

![Screenshot](https://github.com/user-attachments/assets/a7081763-e507-48a0-9c93-6f17f0e1205b)

## Overview
This aims to be a simple & small application that's a containerised web gui for [yamadashy/repopack](https://github.com/yamadashy/repopack).

## Docker Run Command
If you prefer to run the container using `docker run`, use the following command:
```bash
docker run -d --name repopack-ui \
  -p 32123:32123 \
  ziadhorat/repopack-ui
```
Open a web browser and navigate to `http://container-ip:32123`.

## Deploy with docker compose

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

## Local development (docker compose)

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

## TODO
- Implement config options (So we can do stuff like ignore secrets).
  
## Contributing
Feel free to submit issues, feature or pull requests. 
All contributions are welcome!

## License
This project is licensed under the MIT License. See the LICENSE file for details.

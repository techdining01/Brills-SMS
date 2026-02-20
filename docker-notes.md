## Docker Syntax and Usage

### 1. Dockerfile Basics

- `FROM <image>`  
  Sets the base image.
  ```dockerfile
  FROM python:3.12-slim
  ```

- `WORKDIR <path>`  
  Changes the working directory inside the image.
  ```dockerfile
  WORKDIR /app
  ```

- `COPY <src> <dest>`  
  Copies files from the build context into the image.
  ```dockerfile
  COPY requirements.txt .
  COPY . .
  ```

- `RUN <command>`  
  Executes a command at build time, and saves the result in the image layer.
  ```dockerfile
  RUN pip install -r requirements.txt
  ```

- `ENV <KEY> <VALUE>`  
  Sets environment variables inside the container.
  ```dockerfile
  ENV DJANGO_SETTINGS_MODULE=Brills-SMS.settings
  ```

- `EXPOSE <port>`  
  Documents which port the container listens on (for information; it does not open the port on the host).
  ```dockerfile
  EXPOSE 8000
  ```

- `CMD ["executable", "arg1", ...]`  
  Default command when the container starts (can be overridden by `docker run`).
  ```dockerfile
  CMD ["gunicorn", "Brills-SMS.wsgi:application", "--bind", "0.0.0.0:8000"]
  ```

- `ENTRYPOINT ["executable", "arg1", ...]`  
  Like `CMD` but harder to override; often used to wrap the main process.
  ```dockerfile
  ENTRYPOINT ["python", "manage.py"]
  CMD ["runserver", "0.0.0.0:8000"]
  ```

### 2. Image Commands

- `docker build -t <name>:<tag> <context>`  
  Build an image from a Dockerfile.
  ```bash
  docker build -t brills-sms:dev .
  ```

- `docker images`  
  List local images.

- `docker rmi <image>`  
  Remove an image.

### 3. Container Commands

- `docker run [options] <image> [command]`  
  Run a new container from an image.
  ```bash
  docker run --name sms-web -p 8000:8000 brills-sms:dev
  ```
  Common options:
  - `-d` – run in background (detached)
  - `--rm` – remove container when it exits
  - `-p host:container` – map host port to container port
  - `-e KEY=VALUE` – set environment variables

- `docker ps` / `docker ps -a`  
  Show running containers / all containers.

- `docker logs <container>`  
  Show container logs. Add `-f` to follow.

- `docker exec -it <container> <command>`  
  Run a command inside a running container (interactive shell).
  ```bash
  docker exec -it sms-web bash
  docker exec -it sms-web python manage.py shell
  ```

- `docker stop <container>` / `docker start <container>`  
  Stop or start containers.

- `docker rm <container>`  
  Remove a stopped container.

### 4. Docker Compose Basics

- `docker compose up`  
  Start all services defined in `docker-compose.yml`.
  ```bash
  docker compose up
  docker compose up -d      # run in background
  ```

- `docker compose down`  
  Stop and remove containers, networks, and anonymous volumes.

- `docker compose down -v`  
  Also remove named volumes (this deletes database data).

- `docker compose logs <service>`  
  View logs for a specific service.

- `docker compose exec <service> <command>`  
  Run commands inside a service container.
  ```bash
  docker compose exec web python manage.py migrate
  docker compose exec web python manage.py createsuperuser
  ```

### 5. Volumes and Data

- `VOLUME <path>` in Dockerfile or volumes in compose keep data outside the container filesystem.
  - Containers can be destroyed and recreated without losing data.
  - To fully reset data (for example the database), remove the volume:
    ```bash
    docker compose down -v
    docker compose up -d
    ```

### 6. Typical Django Workflow in Docker

- Build image:
  ```bash
  docker compose build
  ```

- Start services:
  ```bash
  docker compose up -d
  ```

- Apply migrations:
  ```bash
  docker compose exec web python manage.py migrate
  ```

- Create superuser:
  ```bash
  docker compose exec web python manage.py createsuperuser
  ```

- Run tests:
  ```bash
  docker compose exec web python manage.py test
  ```


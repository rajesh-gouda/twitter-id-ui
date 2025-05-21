docker build -t frontend .
docker run -d --name frontend -p 5006:5006 frontend:latest

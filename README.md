# 🖥️ Twitter Agent Assignment UI

A FastAPI-based web application for assigning Twitter post IDs (`tweet_id`) to specific agent types. The app allows manual tagging of tweets and stores them in MongoDB. It also displays a table of the most recent assignments.

---

## 🌟 Features

- Simple web form to:
  - Input a `tweet_id`
  - Select an agent type (e.g. actor, director, producer)
- Displays a table of recent agent assignments with:
  - Tweet ID
  - Agent type
  - Status (`pending`, `replied`)
  - Timestamps for created and updated times
- Dockerized for easy deployment

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/rajesh-gouda/twitter-id-ui.git
cd twitter-id-ui
```

### 2. Create a .env File
MONGO_HOST=your_mongodb_host
MONGO_PASSWORD=your_mongo_password

### 3. Build and Run with Docker
#### Build the Docker image
docker build -t twitter_ui:latest .

#### Run the container
docker run -d --name twitter_ui -p 5006:5006 twitter_ui:latest





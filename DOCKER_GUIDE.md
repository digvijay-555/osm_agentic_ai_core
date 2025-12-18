# 🐳 Docker Run Guide

Complete guide to running OSM Agentic AI with Docker.

## 📋 Prerequisites

1. **Docker installed** - [Install Docker](https://docs.docker.com/get-docker/)
2. **Docker Compose installed** (usually comes with Docker Desktop)
3. **`.env` file** created in project root
4. **`credentials.json`** file in project root (Google Sheets service account)

## 🚀 Quick Start (Recommended)

### Option 1: Docker Compose (Easiest - Runs Both Services)

This runs both the API and UI services together:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **UI**: http://localhost:8501

---

## 🔧 Individual Docker Builds

### Option 2: Run API Service Only

```bash
# Build the API image
docker build -f Dockerfile.api -t osm-agentic-api .

# Run the container
docker run -d \
  --name osm-agentic-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -v $(pwd)/app:/app/app \
  osm-agentic-api

# View logs
docker logs -f osm-agentic-api

# Stop container
docker stop osm-agentic-api
docker rm osm-agentic-api
```

### Option 3: Run UI Service Only

```bash
# Build the UI image
docker build -f Dockerfile.ui -t osm-agentic-ui .

# Run the container
docker run -d \
  --name osm-agentic-ui \
  -p 8501:8501 \
  osm-agentic-ui

# View logs
docker logs -f osm-agentic-ui

# Stop container
docker stop osm-agentic-ui
docker rm osm-agentic-ui
```

### Option 4: Run Main Dockerfile (API Only)

```bash
# Build the image
docker build -t osm-agentic-ai .

# Run the container
docker run -d \
  --name osm-agentic-ai \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  osm-agentic-ai
```

---

## 📝 Step-by-Step Setup

### Step 1: Create `.env` File

Create a `.env` file in the project root:

```env
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
USER_AGENT=OSMAgenticAI/1.0
```

**Note:** If Ollama is running on a different machine, update `OLLAMA_BASE_URL` accordingly.

### Step 2: Ensure Credentials File Exists

Make sure `credentials.json` is in the project root:
```bash
ls credentials.json
```

### Step 3: Start Ollama (if running locally)

```bash
# Start Ollama server (if not already running)
ollama serve

# In another terminal, pull a model
ollama pull llama2
```

**Note:** If Ollama is in a Docker container or remote server, update the URL in `.env`.

### Step 4: Run Docker

Choose one of the options above. Docker Compose is recommended.

---

## 🐳 Docker Compose Commands

```bash
# Build and start
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f          # All services
docker-compose logs -f api      # API only
docker-compose logs -f ui       # UI only

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Rebuild without cache
docker-compose build --no-cache

# Restart a specific service
docker-compose restart api
docker-compose restart ui
```

---

## 🔍 Troubleshooting

### Issue: Port Already in Use

```bash
# Check what's using the port
lsof -i :8000
lsof -i :8501

# Kill the process or change ports in docker-compose.yml
```

### Issue: Cannot Find .env File

```bash
# Ensure .env file exists in project root
ls -la .env

# Or pass environment variables directly
docker run -e OLLAMA_MODEL=llama2 -e USER_AGENT=MyApp/1.0 ...
```

### Issue: Cannot Find credentials.json

```bash
# Ensure credentials.json exists
ls -la credentials.json

# Check volume mount in docker-compose.yml
```

### Issue: Container Exits Immediately

```bash
# Check logs
docker-compose logs api
docker logs osm-agentic-api

# Common causes:
# - Missing .env file
# - Missing credentials.json
# - Ollama not accessible
```

### Issue: Ollama Connection Error

If Ollama is running on your host machine (not in Docker):

```bash
# For Linux/Mac, use host.docker.internal
# Update .env:
OLLAMA_BASE_URL=http://host.docker.internal:11434

# For Linux, you may need to add:
# --add-host=host.docker.internal:host-gateway
```

Or run Docker with network mode:

```bash
docker run --network="host" ...
```

### View Container Status

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Inspect container
docker inspect osm-agentic-api
```

---

## 🧹 Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi osm-agentic-api osm-agentic-ui

# Remove all unused Docker resources
docker system prune -a

# Remove volumes (if any)
docker volume prune
```

---

## 📊 Health Checks

Docker Compose includes health checks. Verify services are healthy:

```bash
# Check API health
curl http://localhost:8000/docs

# Check UI health
curl http://localhost:8501/_stcore/health

# Check container health status
docker ps
# Look for "healthy" status in STATUS column
```

---

## 🔐 Security Notes

- Never commit `.env` or `credentials.json` to git
- Use Docker secrets in production
- Mount credentials as read-only (`:ro`)
- Use environment variables for sensitive data

---

## 🚀 Production Deployment

For production, consider:

1. **Use Docker secrets** instead of env files
2. **Set resource limits** in docker-compose.yml
3. **Use reverse proxy** (nginx/traefik)
4. **Enable HTTPS**
5. **Use Docker Swarm or Kubernetes** for orchestration

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)


# 🔒 Semgrep → Linear Integration

Automatically create Linear tickets from Semgrep Pro security findings. This containerized application receives webhooks from Semgrep and creates well-formatted issues in your Linear workspace.

## ✨ Features

- 🎯 **Automatic ticket creation** from Semgrep findings
- 🧙 **Setup Wizard** - beautiful GUI for easy configuration
- 🔐 **Webhook signature verification** for security
- 📊 **Severity-based prioritization** (Critical/High → Urgent, Medium → High, etc.)
- 🔄 **Duplicate detection** prevents creating multiple tickets for the same finding
- 🌐 **Status dashboard** for monitoring
- 🐳 **Fully containerized** for simple deployment

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/johnpeterappsectesting/semgrep-linear-integration.git
cd semgrep-linear-integration
```

### 2. Start the Application

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t semgrep-linear .
docker run -d -p 8080:8080 semgrep-linear
```

### 3. Run the Setup Wizard

Open your browser and go to:
```
http://localhost:8080/setup
```

The setup wizard will guide you through:
1. **Enter your Linear API key** - validates and fetches your teams
2. **Select your team** - choose where issues will be created
3. **Select a project** (optional) - assign issues to a specific project
4. **Configure security** - set webhook secret and debug options

### 4. Configure Semgrep Webhook

After completing the wizard, you'll see instructions to:
1. Go to **Semgrep AppSec Platform** → **Settings** → **Integrations**
2. Click **Add** → Select **Webhook**
3. Enter your server URL + `/webhook`
4. Set the Signature Secret (shown in wizard)
5. Enable notifications in **Rules** → **Policies** → **Rule Modes**

---

## 🖥️ Hosting Options

This application needs to be hosted on a server that can receive webhooks from Semgrep. Here are your options:

### Option 1: Railway (Recommended - Free Tier Available)

Railway offers the simplest deployment with a free tier:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Or connect your GitHub repo directly at [railway.app](https://railway.app)

### Option 2: Render (Free Tier Available)

1. Go to [render.com](https://render.com) and sign up
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Environment:** Docker
   - **Plan:** Free (or Starter for always-on)
5. Add environment variables in the dashboard

### Option 3: Fly.io (Free Tier Available)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly auth login
fly launch
fly deploy
```

### Option 4: Google Cloud Run (Pay-per-use)

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/semgrep-linear

# Deploy
gcloud run deploy semgrep-linear \
  --image gcr.io/PROJECT_ID/semgrep-linear \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "LINEAR_API_KEY=xxx,LINEAR_TEAM_ID=xxx"
```

### Option 5: DigitalOcean App Platform

1. Go to [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Select your GitHub repository
4. Choose **Dockerfile** as the build type
5. Add environment variables
6. Deploy

### Option 6: Self-Hosted (VPS/Server)

On any server with Docker:

```bash
# Clone the repository
git clone https://github.com/johnpeterappsectesting/semgrep-linear-integration.git
cd semgrep-linear-integration

# Start with Docker Compose
docker-compose up -d

# Set up a reverse proxy (nginx example)
# Point your domain to the server and configure SSL
```

### Important Notes for Hosting

- **HTTPS Required**: Semgrep webhooks require HTTPS. Use a service with built-in SSL or set up a reverse proxy
- **Public URL**: The webhook endpoint must be accessible from the internet
- **Environment Variables**: Set credentials via environment variables, not the .env file in production

---

## 📋 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `LINEAR_API_KEY` | ✅ | Your Linear personal API key |
| `LINEAR_TEAM_ID` | ✅ | Team ID where issues are created |
| `LINEAR_PROJECT_ID` | ❌ | Optional project to assign issues |
| `LINEAR_DEFAULT_PRIORITY` | ❌ | Default priority 1-4 (default: 2) |
| `SEMGREP_WEBHOOK_SECRET` | ❌ | Secret for webhook verification |
| `PORT` | ❌ | Server port (default: 8080) |
| `DEBUG` | ❌ | Enable debug logging (default: false) |

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Status dashboard |
| `/setup` | GET | Setup wizard |
| `/health` | GET | Health check (for load balancers) |
| `/webhook` | POST | Semgrep webhook receiver |
| `/api/teams` | GET | List available Linear teams |
| `/api/projects/<team_id>` | GET | List projects for a team |

## 📝 Issue Format

Created issues include:
- **Title:** `[Semgrep] SEVERITY: Rule Name in repo-name`
- **Description:** 
  - Finding details and ID
  - Rule information
  - File location with line numbers
  - Code snippet (if available)
  - Link to code in repository
  - Remediation guidance

## 🔒 Security Considerations

1. **Webhook Verification:** Set `SEMGREP_WEBHOOK_SECRET` to verify incoming requests
2. **API Key Security:** Never commit `.env` files; use secrets management in production
3. **Network Security:** Always deploy behind HTTPS
4. **Non-root Container:** The container runs as a non-root user

## 🏗️ Production Deployment Examples

### Using Docker Compose with Traefik

```yaml
version: "3.8"
services:
  semgrep-linear:
    build: .
    environment:
      - LINEAR_API_KEY=${LINEAR_API_KEY}
      - LINEAR_TEAM_ID=${LINEAR_TEAM_ID}
      - SEMGREP_WEBHOOK_SECRET=${SEMGREP_WEBHOOK_SECRET}
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.semgrep-linear.rule=Host(`semgrep-linear.example.com`)"
      - "traefik.http.routers.semgrep-linear.tls.certresolver=letsencrypt"
```

### On Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: semgrep-linear
spec:
  replicas: 2
  selector:
    matchLabels:
      app: semgrep-linear
  template:
    metadata:
      labels:
        app: semgrep-linear
    spec:
      containers:
      - name: app
        image: semgrep-linear:latest
        ports:
        - containerPort: 8080
        envFrom:
        - secretRef:
            name: semgrep-linear-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
```

## 🐛 Troubleshooting

### Issues not being created

1. Check the logs: `docker-compose logs -f`
2. Verify Linear connection at `http://localhost:8080`
3. Ensure webhook is enabled in Semgrep
4. Check that LINEAR_TEAM_ID is correct

### Webhook signature errors

1. Ensure `SEMGREP_WEBHOOK_SECRET` matches Semgrep's configured secret
2. Check for trailing whitespace in the secret

### Connection refused

1. Ensure your server is accessible from the internet
2. Check firewall rules allow port 8080 (or your configured port)
3. Verify HTTPS is properly configured

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ for security teams

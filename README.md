# 🔒 Semgrep → Linear Integration

Automatically create Linear tickets from Semgrep Pro security findings. This containerized application receives webhooks from Semgrep and creates well-formatted issues in your Linear workspace.

## ✨ Features

- 🎯 **Automatic ticket creation** from Semgrep findings
- 🔐 **Webhook signature verification** for security
- 📊 **Severity-based prioritization** (Critical/High → Urgent, Medium → High, etc.)
- 🔄 **Duplicate detection** prevents creating multiple tickets for the same finding
- 🌐 **Status dashboard** for easy configuration and monitoring
- 🐳 **Fully containerized** for simple deployment

## 🚀 Quick Start

### 1. Clone and Configure

```bash
# Navigate to the project directory
cd LinearIntegration

# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### 2. Get Your Credentials

#### Linear API Key
1. Go to Linear → **Settings** → **API**
2. Click **Create key** under "Personal API keys"
3. Copy the key (starts with `lin_api_`)

#### Linear Team ID
1. Start the application (step 3)
2. Visit `http://localhost:8080`
3. Your teams and their IDs will be displayed

### 3. Start the Application

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t semgrep-linear .
docker run -d -p 8080:8080 --env-file .env semgrep-linear
```

### 4. Configure Semgrep Webhook

1. Go to Semgrep AppSec Platform → **Settings** → **Integrations**
2. Click **Add** → Select **Webhook**
3. Configure:
   - **Name:** Linear Integration
   - **Webhook URL:** `https://your-server.com/webhook`
   - **Signature Secret:** (optional, but recommended)
4. Click **Subscribe**
5. Go to **Rules** → **Policies** → **Rule Modes**
6. Enable webhook notifications for desired rule modes

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
3. **Network Security:** Deploy behind HTTPS (use a reverse proxy like nginx or Cloudflare)
4. **Non-root Container:** The container runs as a non-root user

## 🏗️ Production Deployment

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
3. Verify HTTPS is properly configured if required

## 📄 License

MIT License - feel free to use and modify!

---

Made with ❤️ for security teams


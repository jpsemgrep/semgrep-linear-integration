import logging
from flask import Flask, request, jsonify, render_template
from .config import config
from .linear_client import LinearClient
from .webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize clients
linear_client = LinearClient(config.LINEAR_API_KEY) if config.LINEAR_API_KEY else None
webhook_handler = WebhookHandler(linear_client) if linear_client else None


@app.route("/", methods=["GET"])
def index():
    """Status page with configuration info."""
    validation_errors = config.validate()
    linear_connected = False
    teams = []
    
    if linear_client and not validation_errors:
        try:
            linear_connected = linear_client.test_connection()
            if linear_connected:
                teams = linear_client.get_teams()
        except Exception as e:
            logger.error(f"Error testing Linear connection: {e}")
    
    return render_template(
        "status.html",
        config=config,
        validation_errors=validation_errors,
        linear_connected=linear_connected,
        teams=teams,
        webhook_configured=bool(config.SEMGREP_WEBHOOK_SECRET)
    )


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    errors = config.validate()
    if errors:
        return jsonify({
            "status": "unhealthy",
            "errors": errors
        }), 503
    
    return jsonify({
        "status": "healthy",
        "linear_connected": linear_client.test_connection() if linear_client else False
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """Main webhook endpoint for Semgrep events."""
    if not webhook_handler:
        return jsonify({"error": "Integration not configured"}), 503
    
    # Verify signature
    signature = request.headers.get("X-Semgrep-Signature-256", "")
    if not webhook_handler.verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401
    
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "Empty payload"}), 400
        
        event_type = payload.get("type", "unknown")
        results = []
        
        if event_type == "semgrep_finding":
            # Single finding event
            result = webhook_handler.process_finding(payload.get("finding", payload))
            results.append(result)
            
        elif event_type == "semgrep_scan":
            # Scan completion event
            result = webhook_handler.process_scan(payload.get("scan", payload))
            results.append(result)
            
            # Process any findings included in the scan
            findings = payload.get("findings", [])
            for finding in findings:
                result = webhook_handler.process_finding(finding)
                results.append(result)
        
        else:
            # Try to process as a finding directly
            if "rule" in payload or "severity" in payload:
                result = webhook_handler.process_finding(payload)
                results.append(result)
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return jsonify({"warning": f"Unknown event type: {event_type}"}), 200
        
        return jsonify({
            "status": "success",
            "processed": len(results),
            "results": results
        })
        
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/teams", methods=["GET"])
def get_teams():
    """Get available Linear teams for configuration."""
    if not linear_client:
        return jsonify({"error": "Linear not configured"}), 503
    
    try:
        teams = linear_client.get_teams()
        return jsonify({"teams": teams})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/projects/<team_id>", methods=["GET"])
def get_projects(team_id: str):
    """Get projects for a specific team."""
    if not linear_client:
        return jsonify({"error": "Linear not configured"}), 503
    
    try:
        projects = linear_client.get_projects(team_id)
        return jsonify({"projects": projects})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_app():
    """Application factory."""
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG)


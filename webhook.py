# AUTHOR= Filipe Soares
# DESCRIPTION= Webhook to listen to my GitHub page and post on Facebook
# PYTHON

import os
import hmac
import hashlib
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Load configuration from environment variables for security
GITHUB_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "your_github_webhook_secret")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "your_facebook_page_id")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "your_page_access_token")

def verify_signature(request_body, signature_header):
    """Verify that the webhook actually came from GitHub using HMAC SHA-256."""
    if not signature_header:
        return False
    sha_name, signature = signature_header.split('=')
    if sha_name != 'sha256':
        return False
    
    mac = hmac.new(GITHUB_SECRET.encode('utf-8'), msg=request_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route("/webhook", methods=["POST"])
def github_webhook():
    signature_header = request.headers.get('X-Hub-Signature-256')
    
    # Verify the payload signature
    if not verify_signature(request.data, signature_header):
        return jsonify({"error": "Invalid signature"}), 403

    event = request.headers.get("X-GitHub-Event", "ping")
    
    # GitHub sends a 'ping' event when you first configure the webhook
    if event == "ping":
        return jsonify({"message": "Pong! Webhook configured successfully."}), 200

    # We only care about repository events
    if event == "repository":
        payload = request.json
        action = payload.get("action")
        
        # Trigger when a repo is created or changed from private to public
        if action in ["created", "publicized"]:
            repo = payload.get("repository", {})
            repo_name = repo.get("name")
            repo_url = repo.get("html_url")
            repo_desc = repo.get("description") or "No description provided."
            
            # Construct the message for Facebook
            message = f"🚀 New open-source repository published!\n\n📁 {repo_name}\n📝 {repo_desc}"
            
            # Post to Facebook Graph API
            success = post_to_facebook(message, repo_url)
            if success:
                return jsonify({"status": "success", "repo": repo_name}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to post to Facebook"}), 500

    return jsonify({"status": "ignored", "event": event}), 200

def post_to_facebook(message, link):
    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    payload = {
        "message": message,
        "link": link,
        "access_token": FB_PAGE_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return True
    else:
        print(f"Facebook API Error: {response.text}")
        return False

if __name__ == "__main__":
    # Run locally on port 5000 (use a tool like ngrok for testing)
    app.run(host="0.0.0.0", port=5000)
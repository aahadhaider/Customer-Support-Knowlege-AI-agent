from flask import Flask, render_template, request, jsonify
from agent import run_agent
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    query = {
        "query_id": f"WEB_{datetime.now().strftime('%H%M%S')}",
        "partner_id": "WEB_USER",
        "query_text": user_message,
        "channel": "web",
        "timestamp": datetime.now().isoformat()
    }

    result = run_agent(query)

    return jsonify({
        "reply": result["draft_reply"],
        "status": result["status"],
        "category": result["category"],
        "escalated": result["escalation"]["required"]
    })

if __name__ == "__main__":
    app.run(debug=True)
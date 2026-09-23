"""
run_human_gate_server.py
Minimal Flask app to run Human Gate phi_os endpoint
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from phi_os.human_gate import human_gate_bp

app = Flask(__name__)
app.register_blueprint(human_gate_bp)

if __name__ == '__main__':
    print("=" * 70)
    print("Starting Human Gate Server")
    print("=" * 70)
    print()
    print("Listening on http://localhost:5001")
    print("Endpoints:")
    print("  POST /api/human_gate/submit")
    print("  POST /api/human_gate/approve")
    print("  POST /api/human_gate/reject")
    print("  GET  /api/human_gate/status/<request_id>")
    print("  GET  /api/human_gate/pending")
    print()
    print("Press Ctrl+C to stop")
    print()

    app.run(host='127.0.0.1', port=5001, debug=False)

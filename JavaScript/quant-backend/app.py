from flask import Flask, request, jsonify
from flask_cors import CORS
from simulation import run_simulation

app = Flask(__name__)
CORS(app)  # Allow requests from frontend (localhost:5173)

@app.route('/')
def home():
    return "Quant Backend is Running!"

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    try:
        result = run_simulation(data)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        print("ERROR during simulation:", str(e))  # <-- This line shows us the real error!
        return jsonify({"status": "error", "message": str(e)}), 500


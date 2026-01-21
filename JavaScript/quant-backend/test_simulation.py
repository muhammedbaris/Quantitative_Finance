import requests
import json

# Sample input data
payload = {
    "initial_capital": 1_000_000,
    "public_weights": {
        "SPY": 0.5,
        "TLT": 0.3,
        "VNQ": 0.2
    },
    "returns_data": [
        {"SPY": 0.01, "TLT": -0.005, "VNQ": 0.002},
        {"SPY": 0.007, "TLT": 0.002, "VNQ": -0.003},
        {"SPY": -0.006, "TLT": 0.001, "VNQ": 0.005},
        {"SPY": 0.012, "TLT": 0.003, "VNQ": 0.001},
        {"SPY": -0.008, "TLT": -0.002, "VNQ": 0.002}
    ],
    "private_commitments": [
        {"commitment": 200_000, "start_month": 0},
        {"commitment": 100_000, "start_month": 2}
    ]
}

response = requests.post("http://localhost:5000/simulate", json=payload)

# Show the result
print("Status:", response.status_code)
print("Result:", json.dumps(response.json(), indent=2))

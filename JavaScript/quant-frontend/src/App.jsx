
// Import React and hooks
import React, { useState } from "react";

// Axios is used to make HTTP requests (e.g., to your Flask backend)
import axios from "axios";

// Plot is from react-plotly.js — used to render interactive charts
import Plot from "react-plotly.js";

// Used to parse uploaded CSV return files
import Papa from "papaparse";

function App() {
  // State for user inputs
  const [initialCapital, setInitialCapital] = useState("100000");
  const [publicWeightsInput, setPublicWeightsInput] = useState("SPY:0.6, TLT:0.4");
  const [returnsData, setReturnsData] = useState(null);
  const [csvFilename, setCsvFilename] = useState("");

  // State for private investments
  const [privateCommitment, setPrivateCommitment] = useState("");
  const [privateStartMonth, setPrivateStartMonth] = useState("");
  const [privateInvestments, setPrivateInvestments] = useState([]);

  // State for simulation
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 📂 Handle CSV file upload and parsing
  const handleCSVUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setCsvFilename(file.name);

    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      complete: function (results) {
        const cleaned = results.data.filter((row) =>
          Object.values(row).every((val) => val !== null && val !== "")
        );

        const formatted = cleaned.map((row) => {
          const { Date, ...rest } = row;
          return rest;
        });

        setReturnsData(formatted);
      }
    });
  };

  // ▶️ Run the portfolio simulation
  const handleSimulation = async () => {
    setLoading(true);
    setResult(null);

    try {
      const weightPairs = publicWeightsInput.split(",");
      const weights = {};
      weightPairs.forEach((pair) => {
        const [symbol, weight] = pair.trim().split(":");
        weights[symbol.trim()] = parseFloat(weight);
      });

      const response = await axios.post("http://localhost:5000/simulate", {
        initial_capital: parseFloat(initialCapital),
        public_weights: weights,
        private_commitments: privateInvestments,
        returns_data: returnsData || {
          SPY: Array(120).fill(0.01),
          TLT: Array(120).fill(0.005)
        }
      });

      setResult(response.data.result);
    } catch (error) {
      console.error("Error calling backend:", error);
      alert("Error calling backend. Check terminal/console.");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial, sans-serif", backgroundColor: "#f7f9fc" }}>
      <h1>Quant Portfolio Simulator</h1>

      <div>
        <label>Initial Capital ($):</label><br />
        <input
          type="number"
          value={initialCapital}
          onChange={(e) => setInitialCapital(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "10px" }}>
        <label>Upload Monthly Return CSV:</label><br />
        <input type="file" accept=".csv" onChange={handleCSVUpload} />
        {csvFilename && <p style={{ fontSize: "0.9em", color: "#555" }}>Uploaded: {csvFilename}</p>}
      </div>

      <div style={{ marginTop: "10px" }}>
        <label>Public Weights (e.g. SPY:0.6, TLT:0.4):</label><br />
        <input
          type="text"
          value={publicWeightsInput}
          onChange={(e) => setPublicWeightsInput(e.target.value)}
        />
      </div>

      <div style={{ marginTop: "20px" }}>
        <label><strong>Add Private Investment:</strong></label>
        <div>
          <input
            type="number"
            placeholder="Commitment ($)"
            value={privateCommitment}
            onChange={(e) => setPrivateCommitment(e.target.value)}
          />
          <input
            type="number"
            placeholder="Start Month"
            value={privateStartMonth}
            onChange={(e) => setPrivateStartMonth(e.target.value)}
            style={{ marginLeft: "10px" }}
          />
          <button
            style={{ marginLeft: "10px" }}
            onClick={() => {
              if (privateCommitment && privateStartMonth !== "") {
                const newInvestment = {
                  commitment: parseFloat(privateCommitment),
                  start_month: parseInt(privateStartMonth)
                };
                setPrivateInvestments([...privateInvestments, newInvestment]);
                setPrivateCommitment("");
                setPrivateStartMonth("");
              }
            }}
          >
            Add
          </button>
        </div>

        {privateInvestments.length > 0 && (
          <ul style={{ marginTop: "10px" }}>
            {privateInvestments.map((inv, idx) => (
              <li key={idx}>
                💼 ${inv.commitment} @ Month {inv.start_month}
                <button
                  style={{ marginLeft: "10px" }}
                  onClick={() => {
                    const updated = privateInvestments.filter((_, i) => i !== idx);
                    setPrivateInvestments(updated);
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div style={{ marginTop: "20px" }}>
        <button onClick={handleSimulation} disabled={loading}>
          {loading ? "Running..." : "Run Simulation"}
        </button>
      </div>

      <hr style={{ marginTop: "30px" }} />
      {result && (
        <div>
          <h2>Portfolio Performance</h2>
          <ul>
            {Object.entries(result.metrics).map(([key, value]) => (
              <li key={key}><strong>{key}</strong>: {value}</li>
            ))}
          </ul>

          <Plot
             data={[
              {
                x: [...Array(result.portfolio.total.length).keys()],
                y: result.portfolio.public,
                type: "scatter",
                mode: "lines+markers",
                name: "Public",
                line: { color: "#1f77b4", width: 2 }
              },
              {
                x: [...Array(result.portfolio.total.length).keys()],
                y: result.portfolio.private,
                type: "scatter",
                mode: "lines+markers",
                name: "Private",
                line: { color: "#ff7f0e", width: 2 }
              },
              {
                x: [...Array(result.portfolio.total.length).keys()],
                y: result.portfolio.cash,
                type: "scatter",
                mode: "lines+markers",
                name: "Cash",
                line: { color: "#2ca02c", width: 2 }
              },
              {
                x: [...Array(result.portfolio.total.length).keys()],
                y: result.portfolio.total,
                type: "scatter",
                mode: "lines+markers",
                name: "Total Portfolio",
                line: { color: "#d62728", width: 4 }
              }
            ]}
            layout={{
              title: {
                text: "Portfolio Value Over Time",
                font: { size: 24 }
              },
              width: 950,
              height: 500,
              legend: {
                orientation: "h",
                y: -0.3
              },
              xaxis: {
                title: {
                  text: "Month",
                  font: { size: 16 }
                },
                showgrid: true
              },
              yaxis: {
                title: {
                  text: "Portfolio Value ($)",
                  font: { size: 16 }
                },
                showgrid: true,
                tickprefix: "$",
                hoverformat: ".2f"
              },
              hovermode: "x unified",
              margin: { t: 60, b: 100, l: 60, r: 30 }
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              toImageButtonOptions: {
                format: "png",
                filename: "portfolio_chart",
                height: 500,
                width: 950,
                scale: 1
              }
            }}
          />

        </div>
      )}
    </div>
  );
}

export default App;

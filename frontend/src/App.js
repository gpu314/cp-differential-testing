import React, { useState } from "react";

const BACKEND_URL = "https://cp-differential-testing-backend-docker.onrender.com";

const languages = ["python", "java", "cpp"];

export default function DifferentialTester() {
  const [inputSpec, setInputSpec] = useState("");
  const [slowLang, setSlowLang] = useState("python");
  const [fastLang, setFastLang] = useState("python");
  const [slowCode, setSlowCode] = useState("");
  const [fastCode, setFastCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function runTests() {
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          inputSpec,
          slowLang,
          fastLang,
          slowCode,
          fastCode,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.message });
    }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 900, margin: "auto", padding: 20, fontFamily: "sans-serif" }}>
      <div style={{ marginBottom: 20 }}>
        <label htmlFor="inputSpec" style={{ fontWeight: "bold", display: "block", marginBottom: 6 }}>
          Input Specification:
        </label>
        <input
          id="inputSpec"
          type="text"
          value={inputSpec}
          onChange={(e) => setInputSpec(e.target.value)}
          placeholder="Describe the input format here"
          style={{
            width: "100%",
            padding: 8,
            fontSize: 16,
            borderRadius: 4,
            border: "1px solid #ccc",
          }}
        />
      </div>

      <div style={{ display: "flex", gap: 20 }}>
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <label style={{ fontWeight: "bold", marginBottom: 6 }}>Correct Solution</label>
          <select
            value={slowLang}
            onChange={(e) => setSlowLang(e.target.value)}
            style={{ marginBottom: 8, padding: 6, fontSize: 14 }}
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
          <textarea
            rows={15}
            value={slowCode}
            onChange={(e) => setSlowCode(e.target.value)}
            placeholder={`Correct ${slowLang} solution`}
            style={{ flexGrow: 1, fontFamily: "monospace", fontSize: 14, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>

        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <label style={{ fontWeight: "bold", marginBottom: 6 }}>Incorrect Solution</label>
          <select
            value={fastLang}
            onChange={(e) => setFastLang(e.target.value)}
            style={{ marginBottom: 8, padding: 6, fontSize: 14 }}
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang.toUpperCase()}
              </option>
            ))}
          </select>
          <textarea
            rows={15}
            value={fastCode}
            onChange={(e) => setFastCode(e.target.value)}
            placeholder={`Incorrect ${fastLang} solution`}
            style={{ flexGrow: 1, fontFamily: "monospace", fontSize: 14, padding: 8, borderRadius: 4, border: "1px solid #ccc" }}
          />
        </div>
      </div>


      <div style={{ marginTop: 20 }}>
        <button
          onClick={runTests}
          disabled={loading}
          style={{
            backgroundColor: "#0070f3",
            color: "white",
            padding: "10px 20px",
            fontSize: 16,
            borderRadius: 5,
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Running..." : "Run Tests"}
        </button>
      </div>

      {result && (
        <div style={{ marginTop: 20, fontFamily: "monospace", whiteSpace: "pre-wrap" }}>
          {"error" in result ? (
            <div style={{ color: "red" }}>Error: {result.error}</div>
          ) : result.match ? (
            <div style={{ color: "green" }}>{result.message}</div>
          ) : (
            <>
              <div style={{ color: "red", fontWeight: "bold" }}>Mismatch found!</div>
              <div><strong>Failed Test Input:</strong>{"\n"}{result.test_input}</div>
              <div><strong>Slow Output:</strong>{"\n"}{result.slow_output}</div>
              <div><strong>Fast Output:</strong>{"\n"}{result.fast_output}</div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
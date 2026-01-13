// This file is not necessary if script is in index.html
// But if you use external app.js, paste the two functions here

async function getSupportResistance() {
  document.getElementById('report-output').innerHTML = '<p>Loading support & resistance...</p>';
  try {
    const res = await fetch('/support-resistance');
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    document.getElementById('report-output').innerHTML = `
      <h3>📌 Current Nifty Levels</h3>
      <p><strong>Spot Price:</strong> ${data.spot}</p>
      <p><strong>Support:</strong> ${data.support}</p>
      <p><strong>Resistance:</strong> ${data.resistance}</p>
      <p><em>${data.logic} • Validity: ${data.validity}</em></p>
      <p><small>${data.disclaimer}</small></p>
    `;
  } catch (err) {
    document.getElementById('report-output').innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
  }
}

async function generateReport() {
  document.getElementById('report-output').innerHTML = '<h3>🔄 Generating AI report... (10-20 seconds)</h3><p>Please wait while we analyze live market data.</p>';
  try {
    const res = await fetch('/generate-report');
    const result = await res.json();
    if (!result.success) throw new Error(result.error || "Failed to generate");
    document.getElementById('report-output').innerHTML = `
      <h3>📈 AI Intraday Options Report</h3>
      <p><strong>Generated:</strong> ${result.generated_at}</p>
      <p><strong>Current Nifty Spot:</strong> ${result.spot} | <strong>ATM Strike:</strong> ${result.atm_strike}</p>
      <hr>
      <div style="white-space: pre-wrap; font-size: 16.5px;">${result.report.replace(/\n/g, '<br>')}</div>
    `;
  } catch (err) {
    document.getElementById('report-output').innerHTML = `<p style="color:red;">⚠️ Error: ${err.message}</p>`;
  }
}

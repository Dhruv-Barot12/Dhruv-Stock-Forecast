<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dhruv Stock Forecast</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); color: #333; min-height: 100vh; }
    .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    h1 { color: #1a5fb4; text-align: center; }
    h2 { color: #0d47a1; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    button { padding: 14px 28px; font-size: 18px; margin: 15px 10px; cursor: pointer; background: #1a5fb4; color: white; border: none; border-radius: 8px; transition: 0.3s; }
    button:hover { background: #0d47a1; transform: translateY(-2px); }
    #report-output { margin-top: 30px; padding: 25px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #1a5fb4; line-height: 1.8; font-size: 16px; }
    .disclaimer { font-size: 13px; color: #666; text-align: center; margin-top: 50px; font-style: italic; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔮 Dhruv Stock Forecast</h1>
    <p style="text-align:center; font-size:18px;">Real-time Nifty 50 Analysis • AI-Powered Intraday Insights</p>

    <h2>📊 Support & Resistance Levels</h2>
    <button onclick="getSupportResistance()">Get Current Levels</button>

    <h2>🤖 AI Intraday Options Strategy Report</h2>
    <p>Get today's high-risk intraday recommendation for Nifty options (Calls vs Puts)</p>
    <button onclick="generateReport()">Generate AI Report Now</button>

    <div id="report-output"></div>

    <div class="disclaimer">
      <strong>Disclaimer:</strong> All information is for educational purposes only. Not financial advice.
      Trading options involves substantial risk of loss. Trade at your own risk.
    </div>
  </div>

  <script>
    async function getSupportResistance() {
      document.getElementById('report-output').innerHTML = '<p>Loading...</p>';
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
      document.getElementById('report-output').innerHTML = '<h3>🔄 Generating AI report... (10-20s)</h3>';
      try {
        const res = await fetch('/generate-report');
        const result = await res.json();
        if (!result.success) throw new Error(result.error || "Failed");
        document.getElementById('report-output').innerHTML = `
          <h3>📈 AI Intraday Options Report</h3>
          <p><strong>Generated:</strong> ${result.generated_at}</p>
          <p><strong>Current Nifty Spot:</strong> ${result.spot} | <strong>ATM Strike:</strong> ${result.atm_strike}</p>
          <hr>
          <div style="white-space: pre-wrap; font-size: 16.5px;">${result.report.replace(/\n/g, '<br>')}</div>
        `;
      } catch (err) {
        document.getElementById('report-output').innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
      }
    }
  </script>
</body>
</html>

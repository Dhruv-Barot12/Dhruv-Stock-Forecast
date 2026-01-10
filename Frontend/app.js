const API = "/trade";

async function loadTrade() {
  const res = await fetch(API);
  const data = await res.json();

  if (data.error) {
    document.getElementById("output").innerText = data.error;
    return;
  }

  document.getElementById("output").innerText =
`📊 Trade Output

Spot: ${data.spot}
ATM: ${data.atm}

Generated: ${data.generated}
Weekly Expiry: ${data.weekly_expiry}
Monthly Expiry: ${data.monthly_expiry}

Final Decision: ${data.decision}
Premium: ₹${data.premium}
Expected Return: ${data.expected_return}
Risk: ${data.risk}

Actionable Summary:
${data.summary}`;
}

async function loadSupport() {
  const res = await fetch(API);
  const data = await res.json();

  if (data.error) {
    document.getElementById("output").innerText = data.error;
    return;
  }

  document.getElementById("output").innerText =
`📈 Support & Resistance

Support Levels:
- ${data.support.join("\n- ")}

Resistance Levels:
- ${data.resistance.join("\n- ")}`;
}

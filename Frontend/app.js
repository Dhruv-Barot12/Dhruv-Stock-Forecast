document.getElementById("tradeBtn").onclick = async () => {
  const res = await fetch("/trade");
  const data = await res.json();

  document.getElementById("output").innerText = `
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
${data.actionable_summary}
`;
};

document.getElementById("srBtn").onclick = () => {
  alert("Support & Resistance feature coming soon.");
};

fetch("/trade")
  .then(res => res.json())
  .then(data => {
    document.getElementById("trade-output").innerText = `
Spot: ${data.spot}
ATM: ${data.atm}

Generated: ${data.generated}
Weekly Expiry: ${data.weekly_expiry}
Monthly Expiry: ${data.monthly_expiry}

${data.strategy_text}
`;
  })
  .catch(err => {
    document.getElementById("trade-output").innerText =
      "Error loading trade data.";
  });

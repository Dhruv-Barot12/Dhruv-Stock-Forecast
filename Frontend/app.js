function loadTrade() {
  fetch("/trade")
    .then(res => res.json())
    .then(data => {
      document.getElementById("trade-output").innerText = `
Spot: ${data.spot}
ATM: ${data.atm}

Generated: ${data.generated}
Weekly Expiry: ${data.weekly_expiry}
Monthly Expiry: ${data.monthly_expiry}

${data.output}
`;
    })
    .catch(() => {
      document.getElementById("trade-output").innerText =
        "Error loading trade data.";
    });
}

function showSR() {
  alert("Support & Resistance feature coming soon.");
}

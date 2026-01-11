// Support & Resistance Button
function supportResistance() {
  const output = document.getElementById("trade-output");

  output.innerText = `
Support & Resistance Levels (NIFTY)

Immediate Support:
• 25,750
• 25,600

Major Support:
• 25,500

Immediate Resistance:
• 25,950
• 26,100

Major Resistance:
• 26,250

Note:
• Breakdown below 25,750 increases downside momentum
• Breakout above 26,100 required for strong bullish continuation
• Use these levels only for intraday reference
`;
}

// 9:30 Trade Button (UNCHANGED)
function runTrade() {
  fetch("/trade")
    .then(res => res.json())
    .then(data => {
      document.getElementById("trade-output").innerText = data.output;
    })
    .catch(() => {
      document.getElementById("trade-output").innerText =
        "Error fetching trade data.";
    });
}

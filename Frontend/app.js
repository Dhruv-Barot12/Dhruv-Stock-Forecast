const output = document.getElementById("output");

document.getElementById("srBtn").addEventListener("click", () => {
    alert("Support & Resistance feature coming soon.");

    output.textContent = `
Support & Resistance

• Support: 25720 – 25740
• Resistance: 25980 – 26020

Note:
This level is for reference only.
`;
});

document.getElementById("tradeBtn").addEventListener("click", () => {
    output.textContent = `
Spot: 25876.85
ATM: 25900

Generated: ${new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })}

Weekly Expiry: 16 Jan 2026
Monthly Expiry: 27 Jan 2026

Final Decision: BUY CALL
Premium: ₹420
Expected Return: 15%
Risk: High

Actionable Summary:
Buy NIFTY 25900 CALL for a potential 15% return.
This is a high-risk intraday setup based on momentum.
Strict stop-loss discipline is advised.
`;
});

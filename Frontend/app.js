async function loadTrade() {
    const res = await fetch("/api/trade");
    const d = await res.json();

    document.getElementById("output").innerHTML = `
        <h3>📊 Trade Output</h3>
        Spot: ${d.spot}<br>
        ATM: ${d.atm}<br><br>

        Generated: ${d.generated}<br>
        Weekly Expiry: ${d.weekly_expiry}<br>
        Monthly Expiry: ${d.monthly_expiry}<br><br>

        Final Decision: ${d.decision}<br>
        Premium: ₹${d.premium}<br>
        Expected Return: ${d.expected_return}<br>
        Risk: ${d.risk}<br><br>

        <b>Actionable Summary:</b><br>
        ${d.summary}
    `;
}

async function loadSR() {
    const res = await fetch("/api/support-resistance");
    const d = await res.json();

    document.getElementById("output").innerHTML = `
        <h3>📌 Support & Resistance</h3>
        Support: ${d.support.join(", ")}<br>
        Resistance: ${d.resistance.join(", ")}
    `;
}

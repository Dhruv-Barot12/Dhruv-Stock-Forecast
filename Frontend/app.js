document.getElementById("loadBtn").addEventListener("click", async () => {
    const box = document.getElementById("output");
    box.style.display = "block";
    box.innerHTML = "Loading...";

    try {
        const res = await fetch("/nifty-930-probability");
        const data = await res.json();

        box.innerHTML = `
            <h2>Intraday Probability Outlook — NIFTY 50</h2>
            <p><strong>Reference Level:</strong> ${data.reference_level}</p>

            <ul>
                <li>Upside: ${data.upside}%</li>
                <li>Downside: ${data.downside}%</li>
                <li>Flat: ${data.flat}%</li>
                <li>High Volatility: ${data.high_volatility}%</li>
            </ul>

            <h3>Actionable Summary</h3>
            <pre>${data.actionable_summary}</pre>

            <small>Generated: ${data.generated_at}</small>
        `;
    } catch (err) {
        box.innerHTML = "❌ Failed to load data.";
    }
});

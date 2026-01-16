// IST Military Time
function updateISTTime() {
    const now = new Date();
    const ist = new Date(
        now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" })
    );
    const h = String(ist.getHours()).padStart(2, "0");
    const m = String(ist.getMinutes()).padStart(2, "0");
    document.getElementById("ist-time").innerText = `${h}:${m}`;
}
setInterval(updateISTTime, 1000);
updateISTTime();

// Fetch 9:30 Trade
document.getElementById("tradeBtn").addEventListener("click", async () => {
    try {
        const res = await fetch("/nifty-930");
        const data = await res.json();

        document.getElementById("refLevel").innerText = data.reference_level;
        document.getElementById("upside").innerText = data.upside;
        document.getElementById("downside").innerText = data.downside;
        document.getElementById("flat").innerText = data.flat;
        document.getElementById("volatility").innerText = data.high_volatility;
        document.getElementById("summaryText").innerText = data.actionable_summary;
        document.getElementById("generatedAt").innerText = data.generated_at;

        document.getElementById("resultCard").classList.remove("hidden");
    } catch (e) {
        alert("API not responding. Please check backend.");
    }
});

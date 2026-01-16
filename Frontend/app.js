// -------- IST MILITARY TIME --------
function updateISTTime() {
    const now = new Date();
    const ist = new Date(
        now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" })
    );

    const h = String(ist.getHours()).padStart(2, "0");
    const m = String(ist.getMinutes()).padStart(2, "0");
    const s = String(ist.getSeconds()).padStart(2, "0");

    document.getElementById("militaryTime").innerText = `${h}:${m}:${s}`;
}
setInterval(updateISTTime, 1000);
updateISTTime();

// -------- BUTTON CLICK --------
document.getElementById("tradeBtn").addEventListener("click", async () => {
    try {
        const res = await fetch("/nifty-930");
        const data = await res.json();

        document.getElementById("referenceLevel").innerText = data.reference_level;
        document.getElementById("upside").innerText = data.upside + "%";
        document.getElementById("downside").innerText = data.downside + "%";
        document.getElementById("flat").innerText = data.flat + "%";
        document.getElementById("volatility").innerText = data.high_volatility + "%";
        document.getElementById("summaryText").innerText = data.summary;
        document.getElementById("generatedAt").innerText = data.generated_at;

        document.getElementById("resultCard").classList.remove("hidden");

    } catch (err) {
        alert("API Error. Check backend.");
        console.error(err);
    }
});

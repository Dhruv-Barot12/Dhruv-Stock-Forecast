document.getElementById("tradeBtn").addEventListener("click", loadTrade);

async function loadTrade() {
    try {
        const res = await fetch("/nifty-930");
        const data = await res.json();

        document.getElementById("reference").innerText = data.reference;
        document.getElementById("upside").innerText = data.upside + "%";
        document.getElementById("downside").innerText = data.downside + "%";
        document.getElementById("flat").innerText = data.flat + "%";
        document.getElementById("volatility").innerText = data.volatility + "%";
        document.getElementById("summary").innerText = data.summary;
        document.getElementById("generated").innerText = data.generated_at;

    } catch (err) {
        alert("Failed to load 9:30 data. Check API.");
        console.error(err);
    }
}

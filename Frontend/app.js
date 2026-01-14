document.getElementById("loadBtn").addEventListener("click", async () => {
    const res = await fetch("/nifty-930-probability");
    const data = await res.json();

    document.getElementById("output").style.display = "block";

    document.getElementById("ref").innerText = data.reference_level;
    document.getElementById("up").innerText = data.probabilities.upside;
    document.getElementById("down").innerText = data.probabilities.downside;
    document.getElementById("flat").innerText = data.probabilities.flat;
    document.getElementById("vol").innerText = data.probabilities.high_volatility;

    document.getElementById("summary").innerText = data.actionable_summary;
    document.getElementById("time").innerText = data.generated_at;
});

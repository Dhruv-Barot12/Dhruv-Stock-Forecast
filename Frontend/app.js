async function loadProbability() {
    const res = await fetch("/api/nifty-930");
    const data = await res.json();

    document.getElementById("ref").innerText = data.reference_level;
    document.getElementById("up").innerText = data.upside;
    document.getElementById("down").innerText = data.downside;
    document.getElementById("flat").innerText = data.flat;
    document.getElementById("vol").innerText = data.high_volatility;
    document.getElementById("summary").innerText = data.actionable_summary;
    document.getElementById("time").innerText = "Generated at: " + data.generated_at;

    document.getElementById("result").style.display = "block";
}

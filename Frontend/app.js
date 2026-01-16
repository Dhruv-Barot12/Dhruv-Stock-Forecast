async function loadTrade() {
    try {
        const res = await fetch("/trade");
        const data = await res.json();

        // Show card
        document.getElementById("resultCard").classList.remove("hidden");

        // Safe fallback helper
        const safe = (val, fallback = "—") =>
            val !== undefined && val !== null && val !== "" ? val : fallback;

        document.getElementById("refLevel").innerText =
            safe(data.reference_level);

        document.getElementById("upside").innerText =
            safe(data.upside) + "%";

        document.getElementById("downside").innerText =
            safe(data.downside) + "%";

        document.getElementById("flat").innerText =
            safe(data.flat) + "%";

        document.getElementById("volatility").innerText =
            safe(data.high_volatility) + "%";

        // 🔥 FIXED SUMMARY (NO UNDEFINED EVER)
        document.getElementById("summary").innerText =
            safe(
                data.actionable_summary,
                "No trade advised. Market conditions unclear."
            );

        document.getElementById("generatedAt").innerText =
            safe(data.generated_at);

    } catch (err) {
        alert("Failed to load trade data");
        console.error(err);
    }
}

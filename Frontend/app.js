document.getElementById("loadBtn").addEventListener("click", async () => {
    try {
        const res = await fetch("/nifty-930-probability");
        const data = await res.json();

        document.getElementById("probabilityCard").classList.remove("hidden");

        document.getElementById("title").innerText = data.title;
        document.getElementById("reference").innerText = data.reference_level;

        document.getElementById("upside").innerText = data.probabilities.upside;
        document.getElementById("downside").innerText = data.probabilities.downside;
        document.getElementById("flat").innerText = data.probabilities.flat;
        document.getElementById("volatility").innerText = data.probabilities.high_volatility;

        document.getElementById("strategy").innerText =
            data.actionable_summary.strategy + " — " + data.actionable_summary.reason;

        document.getElementById("strikes").innerText =
            data.actionable_summary.recommended_strikes.join(", ");

        document.getElementById("premium").innerText =
            data.actionable_summary.expected_premium_range;

        document.getElementById("success").innerText =
            data.actionable_summary.probability_of_success;

        document.getElementById("time").innerText = data.generated_at;

    } catch (err) {
        alert("Failed to load probability data");
        console.error(err);
    }
});

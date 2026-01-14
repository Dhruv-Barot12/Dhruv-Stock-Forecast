document.getElementById("loadBtn").addEventListener("click", loadData);

function loadData() {
    fetch("/nifty-930-probability")
        .then(res => res.json())
        .then(data => {
            document.getElementById("output").classList.remove("hidden");

            document.getElementById("title").innerText = data.title;
            document.getElementById("ref").innerText = data.reference_level;

            document.getElementById("upside").innerText = data.upside;
            document.getElementById("downside").innerText = data.downside;
            document.getElementById("flat").innerText = data.flat;
            document.getElementById("vol").innerText = data.high_volatility;

            document.getElementById("summary").innerText = data.actionable_summary;
            document.getElementById("time").innerText = data.generated_at;
        })
        .catch(err => {
            alert("Failed to load data");
            console.error(err);
        });
}

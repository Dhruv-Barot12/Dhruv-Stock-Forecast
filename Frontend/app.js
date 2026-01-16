function loadTrade() {
    fetch("/api/nifty-930")
        .then(res => res.json())
        .then(data => {
            document.getElementById("result").classList.remove("hidden");
            document.getElementById("title").innerText = data.index + " – 9:30 AM Outlook";
            document.getElementById("ref").innerText = data.reference;
            document.getElementById("up").innerText = data.upside;
            document.getElementById("down").innerText = data.downside;
            document.getElementById("flat").innerText = data.flat;
            document.getElementById("vol").innerText = data.volatility;
            document.getElementById("summary").innerText = data.summary;
            document.getElementById("time").innerText = "Generated: " + data.generated;
        })
        .catch(() => alert("API Error"));
}

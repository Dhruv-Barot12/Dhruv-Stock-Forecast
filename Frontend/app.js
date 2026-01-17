const btn = document.getElementById("tradeBtn");

btn.onclick = async () => {
  btn.innerText = "⏳ Loading...";
  btn.disabled = true;

  const res = await fetch("/nifty-930");
  const data = await res.json();

  document.getElementById("ref").innerText = data.reference ?? "—";
  document.getElementById("up").innerText = data.upside ? data.upside + "%" : "—";
  document.getElementById("down").innerText = data.downside ? data.downside + "%" : "—";
  document.getElementById("flat").innerText = data.flat ? data.flat + "%" : "—";
  document.getElementById("vol").innerText = data.volatility ? data.volatility + "%" : "—";
  document.getElementById("summary").innerText = data.summary || "—";
  document.getElementById("time").innerText = data.generated_at || "—";

  btn.innerText = "📊 Execute 9:30 Trade";
  btn.disabled = false;
};

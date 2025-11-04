async function loadResults() {
  const res = await fetch("../data/results.json");
  const data = await res.json();
  renderSidebar(data);
  updateStats(data);
  renderChart(data);
}

function renderSidebar(data) {
  const list = document.getElementById("testList");
  list.innerHTML = "";
  data.slice().reverse().forEach(test => {
    const li = document.createElement("li");
    li.className = test.status === "SUCESSO" ? "success" :
                   test.status === "FALHA" ? "fail" : "warning";
    li.textContent = `${test.icone} ${test.nome}`;
    li.onclick = () => showDetails(test);
    list.appendChild(li);
  });
}

function updateStats(data) {
  const success = data.filter(t => t.status === "SUCESSO").length;
  const fail = data.filter(t => t.status === "FALHA").length;
  const userErr = data.filter(t => t.status === "ERRO_USUARIO").length;
  const total = data.length;

  document.getElementById("successCount").textContent = success;
  document.getElementById("failCount").textContent = fail;
  document.getElementById("userErrorCount").textContent = userErr;
  document.getElementById("totalTests").textContent = total;
}

function renderChart(data) {
  const ctx = document.getElementById("statusChart").getContext("2d");
  const counts = {
    success: data.filter(t => t.status === "SUCESSO").length,
    fail: data.filter(t => t.status === "FALHA").length,
    user: data.filter(t => t.status === "ERRO_USUARIO").length
  };

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Sucesso", "Falha", "Erro Usuário"],
      datasets: [{
        data: [counts.success, counts.fail, counts.user],
        backgroundColor: ["#28C76F", "#EA5455", "#FF9F43"]
      }]
    },
    options: { responsive: true, cutout: "70%" }
  });
}

function showDetails(test) {
  const details = document.getElementById("testDetails");
  details.innerHTML = `
    <h3>${test.icone} ${test.nome}</h3>
    <p><b>Status:</b> ${test.status}</p>
    <p><b>Executado em:</b> ${test.data_execucao}</p>
    <p><b>Duração:</b> ${test.duracao}s</p>
    <h4>Etapas:</h4>
    <pre>${test.etapas.join("\n")}</pre>
    ${test.erro ? `<p><b>Erro:</b> ${test.erro}</p>` : ""}
    ${test.screenshot ? `<img src="../reports/${test.screenshot}" style="max-width:100%;border-radius:10px;">` : ""}
  `;
}

loadResults();

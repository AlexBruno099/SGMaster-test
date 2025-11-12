window.reportData = [];
let statusChart, timeChart;

async function carregarDados() {
  try {
    const res = await fetch('../data/results.json?' + Date.now());
    if (!res.ok) throw new Error("Não foi possível acessar results.json");
    const data = await res.json();
    window.reportData = data;

    const success = data.filter(d => d.status === "SUCESSO").length;
    const fail = data.filter(d => d.status === "FALHA").length;
    const avg = (data.reduce((a, b) => a + (b.duracao || 0), 0) / (data.length || 1)).toFixed(2);

    document.getElementById('successCount').textContent = success;
    document.getElementById('failCount').textContent = fail;
    document.getElementById('avgTime').textContent = avg + "s";

    const testList = document.getElementById('testList');
    testList.innerHTML = data.map(t => `
      <div class="p-2 border border-gray-200 dark:border-gray-700 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 flex justify-between items-center transition"
           onclick="mostrarDetalhes('${t.id}')">
        <span>${t.icone || '🧪'} ${t.nome}</span>
        <span class="${t.status === 'SUCESSO' ? 'text-green-500 font-semibold' : 'text-red-500 font-semibold'}">${t.status}</span>
      </div>
    `).join('');

    if (statusChart) statusChart.destroy();
    statusChart = new Chart(document.getElementById('statusChart'), {
      type: 'doughnut',
      data: {
        labels: ['Sucesso', 'Falha'],
        datasets: [{
          data: [success, fail],
          backgroundColor: ['#22c55e', '#ef4444']
        }]
      },
      options: {
        animation: { duration: 800, easing: 'easeInOutQuart' },
        plugins: { legend: { position: 'bottom' } }
      }
    });

    if (timeChart) timeChart.destroy();
    timeChart = new Chart(document.getElementById('timeChart'), {
      type: 'line',
      data: {
        labels: data.map(t => t.data_execucao),
        datasets: [{
          label: 'Tempo (s)',
          data: data.map(t => t.duracao),
          borderColor: '#3b82f6',
          tension: 0.3,
          fill: false
        }]
      },
      options: {
        animation: { duration: 800, easing: 'easeInOutQuart' },
        plugins: { legend: { position: 'bottom' } }
      }
    });

  } catch (err) {
    console.error("❌ Erro ao carregar dados:", err);
    document.getElementById('details').innerHTML = `
      <div class="text-red-500 dark:text-red-400">
        ⚠️ Erro ao carregar o arquivo de resultados.<br>
        Verifique se o caminho <b>data/results.json</b> existe e contém dados válidos.
      </div>
    `;
  }
}

function mostrarDetalhes(id) {
  const t = window.reportData.find(x => x.id === id);
  if (!t) {
    document.getElementById('details').innerHTML = `
      <h3 class="text-lg font-semibold text-red-600">Erro</h3>
      <p>Não foi possível encontrar o teste com ID <b>${id}</b>.</p>
    `;
    return;
  }

  const iaDescricao = gerarDescricaoIA(t);

  document.getElementById('details').innerHTML = `
    <h3 class="text-xl font-semibold mb-2">${t.icone || '🧪'} ${t.nome}</h3>
    <span class="${t.status === 'SUCESSO' ? 'text-green-500 font-semibold' : 'text-red-500 font-semibold'}">${t.status}</span>
    <p class="mt-2"><b>Executado em:</b> ${t.data_execucao}</p>
    <p><b>Duração:</b> ${t.duracao}s</p>
    ${t.erro ? `<p class="text-red-500 mt-2"><b>Erro:</b> ${t.erro}</p>` : ""}
    <h4 class="font-semibold mt-4">Etapas:</h4>
    <pre class="bg-gray-100 dark:bg-gray-900 p-3 rounded text-sm leading-5 overflow-x-auto whitespace-pre-wrap">${t.etapas?.join('\n') || "Sem etapas registradas"}</pre>
    ${t.screenshot ? `<img src="../${t.screenshot}" class="mt-3 w-1/2">` : ""}
    <div class="mt-4 bg-blue-50 dark:bg-gray-800 border border-blue-200 dark:border-gray-700 p-3 rounded">
      <b>🤖 Análise Inteligente:</b>
      <p class="text-sm mt-1">${iaDescricao}</p>
    </div>
  `;
}

function gerarDescricaoIA(t) {
  if (t.status === "SUCESSO")
    return `O teste "${t.nome}" executou com sucesso em ${t.duracao}s, validando o fluxo principal sem falhas.`;
  else if (t.erro?.toLowerCase().includes("timeout"))
    return `O teste "${t.nome}" falhou por tempo de espera excedido. Verifique a estabilidade da página ou os seletores.`;
  else
    return `O teste "${t.nome}" apresentou falhas inesperadas. Analise os logs e screenshots para diagnóstico.`;
}

// Atualização automática
carregarDados();
setInterval(carregarDados, 100000);

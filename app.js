/* Observatorio de Idoneidad y Capacidad del Estado.
   Datos cifrados (AES-GCM + PBKDF2). Se descifran en el navegador con la contraseña;
   sin ella, el bundle público no es legible. Render con Chart.js. */
const C = { mut: '#94a3b8', grid: 'rgba(255,255,255,.06)' };
Chart.defaults.color = C.mut; Chart.defaults.borderColor = C.grid;
const colorIce = v => v >= 0.70 ? '#10b981' : v >= 0.45 ? '#f59e0b' : '#f43f5e';
const pill = n => `<span class="pill ${n}">${n}</span>`;
const b64 = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));

async function decrypt(pw, b) {
  const baseKey = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
  const key = await crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt: b64(b.salt), iterations: b.iter, hash: b.hash },
    baseKey, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
  const pt = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(b.iv) }, key, b64(b.ct));
  return JSON.parse(new TextDecoder().decode(pt));
}

document.getElementById('unlock').onclick = async () => {
  const pw = document.getElementById('pw').value;
  const err = document.getElementById('err');
  err.textContent = '';
  if (!pw) { err.textContent = 'Ingresa la contraseña.'; return; }
  try {
    const bundle = await fetch('secure/bundle.enc.json').then(r => r.json());
    const data = await decrypt(pw, bundle);
    document.getElementById('lock').style.display = 'none';
    document.getElementById('app').style.display = 'block';
    render(data);
  } catch (e) {
    err.textContent = 'Contraseña incorrecta o datos no disponibles.';
  }
};

function render({ ice, stats, rotacion, redes, sectores }) {
  renderSectores(sectores || []);
  document.getElementById('meta').textContent =
    `${stats.entidades_con_ice} entidades · ${stats.registros_personal.toLocaleString('es-PE')} registros · generado ${stats.generado}`;

  const niv = stats.por_nivel_ice || {};
  document.getElementById('kpis').innerHTML = [
    ['Entidades con ICE', stats.entidades_con_ice],
    ['ICE medio', stats.ice_medio],
    ['% por mérito (medio)', Math.round(stats.merito_medio * 100) + '%'],
    ['Alto / Medio / Bajo', `${niv.alto || 0} / ${niv.medio || 0} / ${niv.bajo || 0}`],
  ].map(([l, v]) => `<div class="card kpi"><div class="v">${v}</div><div class="l">${l}</div></div>`).join('');

  const top = ice.slice(0, 25);
  new Chart(chTop, { type: 'bar',
    data: { labels: top.map(d => d.nombre.length > 42 ? d.nombre.slice(0, 40) + '…' : d.nombre),
      datasets: [{ data: top.map(d => d.ice), backgroundColor: top.map(d => colorIce(d.ice)) }] },
    options: { indexAxis: 'y', plugins: { legend: { display: false } },
      scales: { x: { max: 1, title: { display: true, text: 'Índice ICE (0–1)' } } } } });

  const reg = stats.por_regimen;
  new Chart(chReg, { type: 'doughnut',
    data: { labels: reg.map(r => r.regimen || '(s/d)'), datasets: [{ data: reg.map(r => r.n),
      backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#a855f7', '#f43f5e', '#64748b', '#14b8a6'] }] },
    options: { plugins: { legend: { position: 'right', labels: { font: { size: 10 } } } } } });

  new Chart(chSca, { type: 'scatter',
    data: { datasets: [{ data: ice.map(d => ({ x: d.meritocracia, y: d.capacidad, n: d.nombre })),
      backgroundColor: ice.map(d => colorIce(d.ice)), pointRadius: 3 }] },
    options: { plugins: { legend: { display: false },
      tooltip: { callbacks: { label: c => `${c.raw.n}: mérito ${c.raw.x}, cap ${c.raw.y}` } } },
      scales: { x: { min: 0, max: 1, title: { display: true, text: 'Meritocracia' } },
        y: { min: 0, max: 1, title: { display: true, text: 'Capacidad' } } } } });

  const tb = document.querySelector('#tbl tbody');
  let sortK = 'ice', asc = false;
  const draw = () => {
    const f = (document.getElementById('q').value || '').toLowerCase();
    tb.innerHTML = ice.filter(d => d.nombre.toLowerCase().includes(f))
      .sort((a, b) => (asc ? 1 : -1) * (a[sortK] > b[sortK] ? 1 : a[sortK] < b[sortK] ? -1 : 0))
      .slice(0, 200).map(d => `<tr><td>${d.nombre}</td><td>${d.categoria || ''}</td>
        <td>${d.ice} ${pill(d.nivel_ice)}</td><td>${d.meritocracia}</td>
        <td>${d.capacidad}</td><td>${(d.n_personal || 0).toLocaleString('es-PE')}</td></tr>`).join('');
  };
  document.querySelectorAll('#tbl th').forEach(th => th.onclick = () => {
    const k = th.dataset.k; asc = sortK === k ? !asc : false; sortK = k; draw();
  });
  document.getElementById('q').oninput = draw; draw();

  document.querySelector('#rot tbody').innerHTML = rotacion.map(r =>
    `<tr><td>${r.entidad}</td><td>${r.cargo_norm}</td><td>${r.nivel}</td><td>${r.personas}</td></tr>`).join('');

  // Red de movilidad: hubs (por PageRank) y vínculos más fuertes
  const hubs = [...ice].filter(d => d.pagerank != null).sort((a, b) => b.pagerank - a.pagerank).slice(0, 20);
  document.querySelector('#hubs tbody').innerHTML = hubs.map(d =>
    `<tr><td>${d.nombre}</td><td>${d.pagerank}</td><td>${d.grado || 0}</td></tr>`).join('');
  document.querySelector('#vinc tbody').innerHTML = (redes || []).slice(0, 40).map(e =>
    `<tr><td>${e.origen_nombre}</td><td>${e.destino_nombre}</td><td>${e.peso}</td></tr>`).join('');
}

const ICONS = { MIMP: 'fa-venus', MIDIS: 'fa-hand-holding-heart', MINEDU: 'fa-graduation-cap', MINSA: 'fa-heart-pulse' };
function renderSectores(sectores) {
  const cont = document.getElementById('sectores');
  if (!cont) return;
  cont.innerHTML = sectores.map(s => {
    const reg = (s.regimen || []).slice(0, 4).map(r => `${r.regimen}: ${r.n}`).join(' · ');
    const ents = (s.top_entidades || []).slice(0, 5).map(e =>
      `<tr><td>${e.nombre}</td><td style="text-align:right">${e.n_personal.toLocaleString('es-PE')}</td><td style="text-align:right">${e.ice ?? '—'}</td></tr>`).join('');
    const cargos = (s.top_cargos_decision || []).slice(0, 5).map(c => `${c.cargo} (${c.n})`).join(' · ');
    return `<div class="card">
      <div style="display:flex;align-items:center;gap:.5rem">
        <i class="fa-solid ${ICONS[s.clave] || 'fa-building'}" style="color:#3b82f6"></i>
        <b>${s.clave}</b> <span class="pill ${s.ice_ponderado >= .70 ? 'alto' : s.ice_ponderado >= .45 ? 'medio' : 'bajo'}">ICE ${s.ice_ponderado}</span>
      </div>
      <div class="muted" style="margin:.2rem 0 .5rem">${s.nombre}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:.3rem;font-size:.8rem">
        <div>👥 Personal: <b>${s.n_personal.toLocaleString('es-PE')}</b></div>
        <div>🏢 Entidades: <b>${s.n_entidades}</b></div>
        <div>⭐ Mérito: <b>${s.merito_ponderado}</b></div>
        <div>🎯 Cargos decisión: <b>${s.n_decision}</b></div>
        ${s.ingreso_promedio ? `<div>💰 Ingreso prom.: <b>S/ ${s.ingreso_promedio.toLocaleString('es-PE')}</b></div>` : ''}
      </div>
      <div class="muted" style="margin:.5rem 0 .2rem"><b>Régimen:</b> ${reg}</div>
      <table style="margin-top:.3rem"><thead><tr><th>Sub-entidad</th><th style="text-align:right">Personal</th><th style="text-align:right">ICE</th></tr></thead><tbody>${ents}</tbody></table>
      <div class="muted" style="margin-top:.4rem"><b>Cargos de decisión top:</b> ${cargos || '—'}</div>
    </div>`;
  }).join('');
}

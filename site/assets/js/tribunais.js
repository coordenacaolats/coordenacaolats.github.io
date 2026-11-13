/* LATS UFRN — Informativo, painel "Em julgamento" e notícias dos tribunais.
   Os dados vêm de data/tribunais.js e data/informativos.js (atualizados pelo robô)
   e de content.js (destaques escolhidos pela equipe). Não precisa editar. */
(function () {
  const T = window.LATS_TRIBUNAIS || { noticias: [], emJulgamento: [] };
  const EDS = window.LATS_INFORMATIVOS || [];
  const C = window.LATS || {};
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s = "") => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const dia = iso => { const d = new Date(iso); return isNaN(d) ? "" : d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" }).replace(".", ""); };
  const diaLongo = iso => { const d = new Date(iso.length === 10 ? iso + "T12:00:00" : iso); return isNaN(d) ? iso : d.toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" }); };
  const TIPOS = { decisao: "Decisão", pauta: "Pauta", nova_acao: "Nova ação", institucional: "Institucional", outros: "Outros" };
  const link = (href, inner, cls = "") => `<a class="${cls}" href="${esc(href)}" target="_blank" rel="noopener">${inner}</a>`;

  // ---------- data da atualização
  const up = $("#atualizado");
  if (up && T.atualizadoEm) up.textContent = `Atualizado em ${new Date(T.atualizadoEm).toLocaleString("pt-BR", { day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" })}`;

  // ---------- painel Em julgamento
  function ficha(f, destaque) {
    const linhas = [["Processo", f.processo], ["Relator(a)", f.relator], ["Placar", f.placar]]
      .map(([k, v]) => `<div><dt>${k}</dt><dd>${v ? esc(v) : "<span>a informar</span>"}</dd></div>`).join("");
    return `<article class="ficha ${f.tribunal === "STJ" ? "stj" : "stf"}">
      <header><span class="trib">${esc(f.tribunal)}</span><span class="st">${esc(f.status || "Em pauta")}</span>${destaque ? '<span class="dest">Destaque LATS</span>' : ""}</header>
      <h3>${esc(f.tema)}</h3>
      <dl>${linhas}</dl>
      <footer>${f.data ? `<time>${dia(f.data)}</time>` : "<span></span>"}${f.link ? link(f.link, "Ver notícia ↗", "mini-link") : ""}</footer>
    </article>`;
  }
  $$("[data-painel]").forEach(box => {
    const lim = +box.dataset.painel || 99;
    const itens = [...(C.emJulgamentoDestaques || []).map(f => [f, true]), ...(T.emJulgamento || []).map(f => [f, false])].slice(0, lim);
    box.innerHTML = itens.length ? itens.map(([f, d]) => ficha(f, d)).join("") : '<p class="empty">Nenhum caso em pauta identificado nos últimos dias.</p>';
  });

  // ---------- notícias
  function itemNoticia(n) {
    return `<li class="nt ${n.tribunal === "STJ" ? "stj" : "stf"}">
      <time>${dia(n.data)}</time><span class="trib">${esc(n.tribunal)}</span>
      ${link(n.link, esc(n.titulo), "tt")}<span class="tp">${TIPOS[n.tipo] || ""}</span></li>`;
  }
  const feed = $("#feed");
  if (feed) {
    let trib = "Todos", tipo = "decisao";
    const ns = T.noticias || [];
    const bar = (el, opcoes, atual, set) => {
      el.innerHTML = opcoes.map(([v, r]) => `<button class="filter${v === atual ? " active" : ""}" data-v="${v}">${r}</button>`).join("");
      el.onclick = e => { const b = e.target.closest("button"); if (!b) return; $$("button", el).forEach(x => x.classList.toggle("active", x === b)); set(b.dataset.v); paint(); };
    };
    const paint = () => {
      const lista = ns.filter(n => (trib === "Todos" || n.tribunal === trib) && (tipo === "todas" || n.tipo === tipo));
      feed.innerHTML = lista.map(itemNoticia).join("") || '<li class="empty">Nenhuma notícia nesse filtro.</li>';
    };
    bar($("#f-tribunal"), [["Todos", "STF e STJ"], ["STF", "STF"], ["STJ", "STJ"]], trib, v => trib = v);
    bar($("#f-tipo"), [["decisao", "Decisões"], ["pauta", "Pauta"], ["nova_acao", "Novas ações"], ["institucional", "Institucional"], ["todas", "Todas"]], tipo, v => tipo = v);
    paint();
  }
  $$("[data-ultimas]").forEach(box => {
    const lim = +box.dataset.ultimas || 6;
    box.innerHTML = (T.noticias || []).filter(n => n.tipo === "decisao").slice(0, lim).map(itemNoticia).join("") || '<li class="empty">Em breve.</li>';
  });

  // ---------- Informativo LATS
  const alvo = $("#edicao");
  function bloco(titulo, itens) {
    if (!itens || !itens.length) return "";
    return `<div class="ed-bloco"><h4>${titulo}</h4><ol>${itens.map(i => `<li>
      <h5>${i.link ? link(i.link, esc(i.titulo)) : esc(i.titulo)}</h5>${i.resumo ? `<p>${esc(i.resumo)}</p>` : ""}</li>`).join("")}</ol></div>`;
  }
  function edicaoHTML(e) {
    return `<header class="ed-top"><span class="ed-num">Nº ${String(e.numero).padStart(2, "0")}</span>
        <div><span class="eyebrow">Semana de ${diaLongo(e.semana)}</span><h3>${esc(e.titulo)}</h3><p>${esc(e.abertura || "")}</p></div></header>
      <div class="ed-cols">${bloco("Supremo Tribunal Federal", e.stf)}${bloco("Superior Tribunal de Justiça", e.stj)}</div>
      ${bloco("Na pauta", e.pauta)}
      ${e.geradoComIA ? '<p class="ed-ia">Edição elaborada com auxílio de inteligência artificial a partir das notícias oficiais e revisada pela equipe da LATS.</p>' : ""}`;
  }
  function resumoAutomatico() {
    const limite = Date.now() - 7 * 864e5;
    const sem = (T.noticias || []).filter(n => n.tipo === "decisao" && new Date(n.data) >= limite);
    const p = t => sem.filter(n => n.tribunal === t).slice(0, 6).map(n => ({ titulo: n.titulo, link: n.link }));
    return `<header class="ed-top"><span class="ed-num">7d</span>
        <div><span class="eyebrow">Resumo automático</span><h3>As decisões da semana</h3>
        <p>Enquanto a próxima edição do Informativo não sai, veja as principais decisões noticiadas pelos tribunais nos últimos sete dias.</p></div></header>
      <div class="ed-cols">${bloco("Supremo Tribunal Federal", p("STF"))}${bloco("Superior Tribunal de Justiça", p("STJ"))}</div>`;
  }
  if (alvo) {
    const sel = $("#ed-select");
    if (EDS.length) {
      sel.innerHTML = `<label>Edição <select>${EDS.map((e, i) => `<option value="${i}">Nº ${e.numero} · ${diaLongo(e.semana)}</option>`).join("")}</select></label>`;
      $("select", sel).onchange = ev => { alvo.innerHTML = edicaoHTML(EDS[+ev.target.value]); };
      alvo.innerHTML = edicaoHTML(EDS[0]);
    } else {
      alvo.innerHTML = resumoAutomatico();
    }
  }
  // teaser da home
  const tz = $("#ultimo-informativo");
  if (tz) tz.innerHTML = EDS.length
    ? `<span class="eyebrow">Informativo nº ${EDS[0].numero}</span><h3>${esc(EDS[0].titulo)}</h3><p>${esc(EDS[0].abertura || "")}</p>`
    : `<span class="eyebrow">Informativo LATS</span><h3>As decisões da semana no STF e no STJ</h3><p>Toda segunda-feira, um resumo do que os Tribunais Superiores decidiram e do que está na pauta.</p>`;
})();

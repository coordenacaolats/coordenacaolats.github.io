/* LATS UFRN — comportamento do site (não precisa editar) */
(function () {
  const D = window.LATS || {};
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const esc = (s = "") => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const slug = s => String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/\s+/g, "-");
  const ext = url => /^https?:/.test(url) ? ' target="_blank" rel="noopener"' : "";

  const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }), { threshold: .12, rootMargin: "0px 0px -40px 0px" }) : null;

  /* ---------- Ícones ---------- */
  const ICON = {
    instagram: '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zM12 16a4 4 0 110-8 4 4 0 010 8zm6.4-11.8a1.4 1.4 0 100 2.9 1.4 1.4 0 000-2.9z"/></svg>',
    linkedin: '<svg viewBox="0 0 24 24"><path d="M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.4V9h3.4v1.6c.5-.9 1.6-1.8 3.4-1.8 3.6 0 4.3 2.4 4.3 5.5v6.2zM5.3 7.4a2.1 2.1 0 110-4.2 2.1 2.1 0 010 4.2zM7.1 20.5H3.6V9h3.5v11.5zM22.2 0H1.8C.8 0 0 .8 0 1.7v20.6c0 .9.8 1.7 1.8 1.7h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0z"/></svg>',
    youtube: '<svg viewBox="0 0 24 24"><path d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/></svg>'
  };
  const R = D.redes || {};
  $$("[data-social]").forEach(box => {
    box.innerHTML = ["instagram", "linkedin", "youtube"].filter(k => R[k])
      .map(k => `<a href="${esc(R[k])}" target="_blank" rel="noopener" aria-label="${k}">${ICON[k]}</a>`).join("");
  });
  $$("[data-icon]").forEach(el => el.insertAdjacentHTML("afterbegin", ICON[el.dataset.icon] || ""));
  $$("[data-href]").forEach(el => { const v = R[el.dataset.href]; if (v) { el.href = el.dataset.href === "email" ? "mailto:" + v : v; } });
  $$("[data-text]").forEach(el => { const v = R[el.dataset.text]; if (v) el.textContent = v; });

  /* ---------- Header + menu ---------- */
  const header = $(".header");
  const onScroll = () => header && header.classList.toggle("scrolled", scrollY > 60);
  addEventListener("scroll", onScroll, { passive: true }); onScroll();
  const menuBtn = $(".menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      const open = document.body.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", open);
      $$(".overlay nav a").forEach((a, i) => a.style.transitionDelay = open ? (0.25 + i * 0.05) + "s" : "0s");
    });
    $$(".overlay a").forEach(a => a.addEventListener("click", () => document.body.classList.remove("menu-open")));
    addEventListener("keydown", e => e.key === "Escape" && document.body.classList.remove("menu-open"));
  }

  /* ---------- Ondas animadas (inspiradas nas linhas do símbolo) ---------- */
  $$("canvas[data-waves]").forEach(cv => {
    const ctx = cv.getContext("2d");
    const color = cv.dataset.waves || "214,230,242";
    let w, h, t = Math.random() * 100, mx = .5, my = .5;
    const lines = 26;
    const size = () => { const r = devicePixelRatio || 1; w = cv.clientWidth; h = cv.clientHeight; cv.width = w * r; cv.height = h * r; ctx.setTransform(r, 0, 0, r, 0, 0); };
    size(); addEventListener("resize", size);
    cv.parentElement.addEventListener("pointermove", e => { const b = cv.getBoundingClientRect(); mx = (e.clientX - b.left) / b.width; my = (e.clientY - b.top) / b.height; });
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    function draw() {
      ctx.clearRect(0, 0, w, h);
      for (let i = 0; i < lines; i++) {
        const p = i / (lines - 1);
        ctx.beginPath();
        ctx.strokeStyle = `rgba(${color},${0.05 + 0.13 * Math.sin(p * Math.PI)})`;
        ctx.lineWidth = 1;
        for (let x = 0; x <= w; x += 6) {
          const nx = x / w;
          const env = Math.exp(-Math.pow((nx - (0.3 + mx * 0.4)) * 2.3, 2));
          const y = h * (0.62 + (my - .5) * 0.06)
            + Math.sin(nx * 5 + t * 0.6 + p * 1.8) * 46 * env
            + Math.sin(nx * 11 - t * 0.4 + p * 3) * 12
            + (p - 0.5) * 150 * (0.35 + env);
          x ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        }
        ctx.stroke();
      }
      t += 0.008;
      if (!reduce) requestAnimationFrame(draw);
    }
    draw();
  });

  /* ---------- Renderizações ---------- */
  const initials = n => n.replace(/^(Prof\.|Dr\.|Dra\.|Profa\.)\s*/g, "").split(/\s+/).filter(Boolean).map(s => s[0]).slice(0, 2).join("").toUpperCase();
  const fmtDate = d => { if (!d) return ""; if (/^\d{4}$/.test(d)) return d; const dt = new Date(d + "T12:00:00"); return isNaN(dt) ? d : dt.toLocaleDateString("pt-BR", { month: "short", year: "numeric" }).replace(".", ""); };

  function filters(container, items, key, render) {
    if (!container) return;
    const groups = [...new Set(items.map(i => i[key]).filter(Boolean))];
    const bar = container.previousElementSibling && container.previousElementSibling.classList.contains("filters") ? container.previousElementSibling : null;
    const paint = g => { container.innerHTML = items.filter(i => g === "Todos" || i[key] === g).map(render).join("") || '<p class="empty">Em breve.</p>'; observe(container); bindMedia(container); };
    if (bar && groups.length > 1) {
      bar.innerHTML = ["Todos", ...groups].map((g, i) => `<button class="filter${i ? "" : " active"}" data-g="${esc(g)}">${esc(g)}</button>`).join("");
      bar.addEventListener("click", e => { const b = e.target.closest(".filter"); if (!b) return; $$(".filter", bar).forEach(x => x.classList.toggle("active", x === b)); paint(b.dataset.g); });
    }
    paint("Todos");
  }

  // Números
  const st = $("#stats");
  if (st) st.innerHTML = (D.numeros || []).map(n => `<div class="stat reveal"><b>${esc(n.valor)}</b><span>${esc(n.rotulo)}</span></div>`).join("");

  // Membros
  filters($("#members"), D.membros || [], "grupo", m => `
    <article class="member reveal">
      <div class="photo">
        ${m.foto ? `<img src="${esc(m.foto)}" alt="${esc(m.nome)}" loading="lazy">` : `<div class="initials">${esc(initials(m.nome))}</div>`}
        ${(m.linkedin || m.lattes) ? `<div class="links">${m.linkedin ? `<a href="${esc(m.linkedin)}" target="_blank" rel="noopener">LinkedIn</a>` : ""}${m.lattes ? `<a href="${esc(m.lattes)}" target="_blank" rel="noopener">Lattes</a>` : ""}</div>` : ""}
      </div>
      <div><h4>${esc(m.nome)}</h4><p>${esc(m.cargo)}</p></div>
    </article>`);

  // Foto do grupo
  const tp = $("#team-photo");
  if (tp) { const g = D.fotoGrupo; if (g && g.foto) tp.innerHTML = `<button class="ph" data-lightbox="${esc(g.foto)}"><img src="${esc(g.foto)}" alt="${esc(g.legenda || "")}" loading="lazy"></button>${g.legenda ? `<figcaption>${esc(g.legenda)}</figcaption>` : ""}`; else tp.remove(); }

  // Publicações
  filters($("#pubs"), (D.publicacoes || []).slice().sort((a, b) => (b.data || "").localeCompare(a.data || "")), "tipo", p => `
    <a class="pub reveal" href="${esc(p.link || "#")}"${/^https?:|\.pdf$/i.test(p.link || "") ? ' target="_blank" rel="noopener"' : ""}>
      <div class="meta"><b>${esc(p.tipo)}</b><span>${esc(p.tribunal || "")}</span><span>${fmtDate(p.data)}</span></div>
      <div><h3>${esc(p.titulo)}</h3>${p.resumo ? `<p>${esc(p.resumo)}</p>` : ""}
        ${p.autores ? `<div class="authors"><b>Autores</b> ${esc(p.autores)}</div>` : ""}
        ${p.membro ? `<div class="authors"><b>Na LATS</b> ${esc(p.membro)}</div>` : ""}
        ${p.orientacao ? `<div class="authors"><b>Orientação</b> ${esc(p.orientacao)}</div>` : ""}
        ${p.publicadoEm ? `<div class="authors"><b>Publicado em</b> <i>${esc(p.publicadoEm)}</i></div>` : ""}
        ${(p.palavras || []).length ? `<div class="pub-tags">${p.palavras.map(t => `<span>${esc(t)}</span>`).join("")}</div>` : ""}
        ${p.link && !/^#?$/.test(p.link) ? `<span class="pub-pdf">${/\.pdf$/i.test(p.link) ? "Ler o texto completo (PDF) ↗" : "Resumo, sumário e texto completo →"}</span>` : ""}</div>
      <span class="go"><span class="arrow"></span></span>
    </a>`);

  // ---------- Vídeos: detecta YouTube, Drive, Spotify, MP4 e Instagram ----------
  function parseVideo(url) {
    if (!url) return null;
    url = String(url).trim();
    let m;
    if ((m = url.match(/(?:youtu\.be\/|v=|embed\/|shorts\/|live\/)([\w-]{11})/)) || /^[\w-]{11}$/.test(url)) {
      const id = m ? m[1] : url;
      return { kind: "youtube", id, thumb: `https://i.ytimg.com/vi/${id}/hqdefault.jpg` };
    }
    if ((m = url.match(/drive\.google\.com\/file\/d\/([\w-]+)/))) return { kind: "drive", src: `https://drive.google.com/file/d/${m[1]}/preview` };
    if (/open\.spotify\.com\//.test(url)) return { kind: "spotify", src: url.replace("open.spotify.com/", "open.spotify.com/embed/").split("?")[0] };
    if (/instagram\.com\//.test(url)) return { kind: "instagram", href: url };
    if (/\.(mp4|webm|mov)(\?|$)/i.test(url)) return { kind: "file", src: url };
    return { kind: "link", href: url };
  }
  function playerHTML(v, autoplay) {
    if (v.kind === "youtube") return `<iframe src="https://www.youtube-nocookie.com/embed/${v.id}?rel=0${autoplay ? "&autoplay=1" : ""}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
    if (v.kind === "drive") return `<iframe src="${v.src}" allow="autoplay" allowfullscreen></iframe>`;
    if (v.kind === "spotify") return `<iframe class="sp" src="${v.src}" allow="encrypted-media"></iframe>`;
    if (v.kind === "file") return `<video src="${esc(v.src)}" controls ${autoplay ? "autoplay" : ""} playsinline></video>`;
    return "";
  }
  const symbol = "assets/img/simbolo.png";
  function cover(v, capa, tag) {
    const img = capa ? `<img src="${esc(capa)}" alt="" loading="lazy">`
      : (v && v.thumb ? `<img src="${v.thumb}" alt="" loading="lazy">` : `<div class="placeholder"><img src="${symbol}" alt=""></div>`);
    const state = !v ? `<span class="soon">Gravação em breve</span>`
      : (v.kind === "instagram" || v.kind === "link") ? `<span class="soon">Assistir ↗</span>` : `<span class="play"></span>`;
    return `${img}${tag ? `<span class="tag">${esc(tag)}</span>` : ""}${state}`;
  }
  function bindMedia(root) {
    $$("[data-play]", root).forEach(f => f.addEventListener("click", () => {
      const v = parseVideo(f.dataset.play); f.innerHTML = playerHTML(v, true); f.classList.add("playing");
    }, { once: true }));
  }

  // Aulas gravadas
  filters($("#aulas"), D.aulas || [], "categoria", a => {
    const v = parseVideo(a.video);
    const inline = v && ["youtube", "drive", "file"].includes(v.kind);
    const href = (v && v.href) || (!v && a.instagram) || "";
    let frame;
    if (v && v.kind === "spotify") frame = `<div class="spotify">${playerHTML(v)}</div>`;
    else if (inline) frame = `<div class="frame" data-play="${esc(a.video)}">${cover(v, a.capa, a.categoria)}</div>`;
    else if (href) frame = `<a class="frame" href="${esc(href)}" target="_blank" rel="noopener">${cover(v, a.capa, a.categoria)}</a>`;
    else frame = `<div class="frame">${cover(v, a.capa, a.categoria)}</div>`;
    return `<article class="media reveal">${frame}
      ${a.data ? `<span class="media-date">${fmtDate(a.data)}</span>` : ""}
      <h3>${esc(a.titulo)}</h3>${a.palestrantes ? `<p class="who">${esc(a.palestrantes)}</p>` : ""}${a.descricao ? `<p>${esc(a.descricao)}</p>` : ""}
      ${a.instagram ? `<a class="mini-link" href="${esc(a.instagram)}" target="_blank" rel="noopener">Ver no Instagram ↗</a>` : ""}
    </article>`;
  });

  // Podcast — player em destaque + lista de episódios
  const pod = $("#podcast-player");
  if (pod) {
    const eps = D.podcast || [];
    const stage = (e, autoplay) => {
      const v = parseVideo(e.video);
      let media;
      if (v && (v.kind === "instagram" || v.kind === "link")) media = `<a class="frame" href="${esc(v.href)}" target="_blank" rel="noopener">${cover(v, e.capa)}</a>`;
      else if (v && (autoplay || v.kind === "spotify")) media = playerHTML(v, autoplay);
      else if (v) media = `<div class="frame" data-play="${esc(e.video)}">${cover(v, e.capa)}</div>`;
      else media = `<div class="frame">${cover(null, e.capa)}</div>`;
      return `<div class="pod-screen ${v && v.kind === "spotify" ? "audio" : ""}">${media}</div>
        <div class="pod-info"><span class="eyebrow">${esc(e.episodio || "")}${e.data ? " · " + fmtDate(e.data) : ""}${e.duracao ? " · " + esc(e.duracao) : ""}</span>
        <h3>${esc(e.titulo)}</h3>${e.convidados ? `<p class="who">${esc(e.convidados)}</p>` : ""}<p>${esc(e.descricao || "")}</p></div>`;
    };
    pod.innerHTML = eps.length
      ? `<div class="pod-main"></div><ol class="pod-list">${eps.map((e, i) => `
        <li><button data-i="${i}" class="${i ? "" : "active"}"><span class="n">${esc(e.episodio || String(i + 1).padStart(2, "0"))}</span><span class="t">${esc(e.titulo)}<small>${esc(e.convidados || "")}</small></span><span class="st">${e.video ? "▶" : "em breve"}</span></button></li>`).join("")}</ol>`
      : '<p class="empty">Em breve, o primeiro episódio.</p>';
    const main = $(".pod-main", pod);
    const show = (i, ap) => { if (!main) return; main.innerHTML = stage(eps[i], ap); bindMedia(main); };
    show(0, false);
    pod.addEventListener("click", ev => {
      const b = ev.target.closest(".pod-list button"); if (!b) return;
      $$(".pod-list button", pod).forEach(x => x.classList.toggle("active", x === b));
      show(+b.dataset.i, !!eps[+b.dataset.i].video);
    });
  }

  // Formulários
  const forms = $("#forms");
  if (forms) forms.innerHTML = (D.formularios || []).map(f => {
    const s = slug(f.status || "em breve");
    const label = { aberto: "Inscrever-se", "em-breve": "Em breve", encerrado: "Encerrado" }[s] || "Acessar";
    const can = f.link && s !== "em-breve";
    return `<article class="form-card ${f.tema === "stc" ? "stc" : ""} reveal">
      <span class="status ${s}">${esc(f.status)}</span>
      <h3>${esc(f.titulo)}</h3><p>${esc(f.descricao || "")}</p>
      ${f.prazo ? `<span class="prazo">${esc(f.prazo)}</span>` : ""}
      <a class="btn ${can ? "" : "disabled"}" href="${esc(f.link || "#")}"${ext(f.link || "")}>${s === "encerrado" && f.link ? "Saiba mais" : label}<span class="arrow"></span></a>
    </article>`;
  }).join("");

  // Links
  const links = $("#links");
  if (links) links.innerHTML = (D.links || []).map(l => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.titulo)}<i>↗</i></a>`).join("");

  // Instagram
  const ig = $("#ig-feed");
  if (ig) {
    const F = D.instagramFeed || {};
    if (F.beholdFeedId) {
      ig.innerHTML = `<behold-widget feed-id="${esc(F.beholdFeedId)}"></behold-widget>`;
      const s = document.createElement("script"); s.type = "module"; s.src = "https://w.behold.so/widget.js"; document.head.appendChild(s);
    } else if ((F.postsFixos || []).length) {
      ig.className = "ig-embeds";
      ig.innerHTML = F.postsFixos.map(u => `<blockquote class="instagram-media" data-instgrm-permalink="${esc(u)}" data-instgrm-version="14"></blockquote>`).join("");
      const s = document.createElement("script"); s.async = true; s.src = "https://www.instagram.com/embed.js"; document.body.appendChild(s);
    } else {
      const imgs = ["simbolo.png", "simbolo-navy.png", "simbolo-navy.png", "simbolo.png", "simbolo.png", "simbolo-navy.png"];
      ig.className = "ig-fallback";
      ig.innerHTML = imgs.map((im, i) => `<a href="${esc(R.instagram || "#")}" target="_blank" rel="noopener" aria-label="Instagram"><img src="assets/img/${i % 3 === 2 ? "simbolo-navy.png" : "simbolo.png"}" alt=""></a>`).join("");
    }
  }
  // LinkedIn
  const li = $("#li-feed");
  if (li && (D.linkedinPosts || []).length) {
    li.innerHTML = D.linkedinPosts.map(u => `<iframe src="${esc(u)}" loading="lazy" title="Post do LinkedIn" allowfullscreen></iframe>`).join("");
  }

  /* ---------- STC ---------- */
  const S = D.stc || {};
  $$("[data-stc]").forEach(el => { const v = S[el.dataset.stc]; if (v) el.textContent = v; });
  $$("[data-stc-link]").forEach(el => { const v = S[el.dataset.stcLink]; if (v) { el.href = v; if (/^https?:/.test(v)) { el.target = "_blank"; el.rel = "noopener"; } } else el.classList.add("disabled"); });
  const roles = $("#roles");
  if (roles) roles.innerHTML = (S.papeis || []).map((p, i) => `<div class="role reveal"><span class="num">${["I", "II", "III", "IV", "V", "VI"][i] || i + 1}</span><h3>${esc(p.titulo)}</h3>${p.vagas ? `<span class="vagas">${esc(p.vagas)}</span>` : ""}<p>${esc(p.texto)}</p></div>`).join("");
  const func = $("#funcionamento"); if (func && S.funcionamento) func.textContent = S.funcionamento;
  const caso = $("#caso");
  if (caso && S.caso) caso.innerHTML = `<span class="eyebrow">O caso desta edição</span><h3>${esc(S.caso.titulo)}</h3><p>${esc(S.caso.texto)}</p>`;
  const tl = $("#timeline");
  if (tl) tl.innerHTML = (S.cronograma || []).map(c => `<div class="tl-item reveal"><span class="d">${esc(c.data)}</span><div><h3>${esc(c.titulo)}</h3><p>${esc(c.texto)}</p></div></div>`).join("");

  // História
  const hist = $("#historia-tl");
  if (hist) hist.innerHTML = (S.historia || []).map((h, i) => `<div class="h-item reveal"><span class="h-year">${esc(h.ano)}</span><span class="h-num">${["I", "II", "III", "IV", "V", "VI", "VII", "VIII"][i] || ""}</span><h3>${esc(h.titulo)}</h3><p>${esc(h.texto)}</p></div>`).join("");
  // Acervo por edição
  const tabs = $("#ed-tabs"), panel = $("#ed-panel"), EDS = S.edicoes || [];
  if (tabs && panel) {
    if (!EDS.length) { tabs.closest(".arquivo").remove(); }
    else {
      tabs.innerHTML = EDS.map((e, i) => `<button role="tab" data-i="${i}" class="${i ? "" : "active"}"><b>${esc(e.numero)}</b><span>${esc(e.ano || "")}</span></button>`).join("");
      const paint = i => {
        const e = EDS[i], f = e.fotos || [];
        panel.innerHTML = `<div class="ed-info"><span class="ed-big">${esc(e.numero)}</span>
            <div><span class="eyebrow">${esc(e.numero)} edição${e.ano ? " · " + esc(e.ano) : ""}</span><h4>${esc(e.tema)}</h4><p>${esc(e.texto || "")}</p>
            <div class="ed-foot">${e.credito ? `<small>${esc(e.credito)}</small>` : ""}${e.instagram ? `<a class="mini-link" href="${esc(e.instagram)}" target="_blank" rel="noopener">Ver no Instagram ↗</a>` : ""}</div></div></div>
          <div class="ed-grid n${Math.min(f.length, 5)}">${f.map(src => `<button class="ph" data-lightbox="${esc(src)}"><img src="${esc(src)}" alt="${esc(e.numero)} edição da STC" loading="lazy"></button>`).join("")}</div>`;
        panel.classList.remove("swap"); void panel.offsetWidth; panel.classList.add("swap");
      };
      tabs.addEventListener("click", ev => { const b = ev.target.closest("button"); if (!b) return; $$("button", tabs).forEach(x => x.classList.toggle("active", x === b)); paint(+b.dataset.i); });
      paint(0);
    }
  }

  // Hall da STC
  const hall = $("#hall-tabela");
  if (hall) {
    const eds = S.edicoes || [];
    const atual = { numero: S.edicao, ano: "2026", tema: S.caso ? (S.caso.tema || S.caso.titulo) : "", decisao: S.decisaoAtual || "", destaques: S.destaquesAtuais || [] };
    const linhas = [atual, ...eds].filter(e => e.numero);
    hall.innerHTML = `<div class="hall-row hall-h"><span>Edição</span><span>Caso julgado</span><span>Decisão do Plenário</span><span>Destaques</span></div>` +
      linhas.map(e => `<div class="hall-row reveal">
        <span class="hall-ed"><b>${esc(e.numero)}</b><small>${esc(e.ano || "")}</small></span>
        <span class="hall-tema">${esc(e.tema || "")}</span>
        <span class="hall-dec">${e.decisao ? esc(e.decisao) : `<i>${e === atual ? "Sessão em " + esc(S.dataSessao || "breve") : "a registrar"}</i>`}</span>
        <span class="hall-dest">${(e.destaques || []).length ? e.destaques.map(d => `<em>${esc(d.premio)}</em> ${esc(d.nome)}`).join("<br>") : "<i>a registrar</i>"}</span>
      </div>`).join("");
  }

  // Entrevistas
  const ent = $("#entrevistas-lista");
  if (ent) {
    const L = S.entrevistas || [];
    const convite = `<a class="ent-convite reveal" href="${esc(S.entrevistasConvite || "#")}" target="_blank" rel="noopener">
        <img src="assets/img/simbolo-navy.png" alt=""><b>Você participou da STC?</b><span>Conte para a LATS onde a tribuna levou você. Sua história pode inspirar a próxima geração.</span><em>Quero participar ↗</em></a>`;
    ent.innerHTML = L.map(p => p.video ? `<article class="ent ent-video reveal">
        <div class="ent-player" data-video="${esc(p.video)}">
          <img src="${esc(p.capa || "")}" alt="Depoimento de ${esc(p.nome)}" loading="lazy">
          <button class="ent-play" aria-label="Assistir ao depoimento de ${esc(p.nome)}"></button>
          <span class="ent-tag">Depoimento</span>
        </div>
        <div class="ent-txt">${p.area ? `<span class="ent-area">${esc(p.area)}</span>` : ""}<h3>${esc(p.nome)}</h3>
          ${p.hoje ? `<p class="ent-hoje">${esc(p.hoje)}</p>` : ""}<p class="ent-stc">${esc(p.funcaoSTC || "")}${p.edicao ? " · " + esc(p.edicao) : ""}</p>
          ${p.citacao ? `<blockquote>“${esc(p.citacao)}”</blockquote>` : ""}</div>
      </article>` : `<article class="ent reveal">
        <div class="ent-foto">${p.foto ? `<img src="${esc(p.foto)}" alt="${esc(p.nome)}" loading="lazy">` : `<span>${esc((p.nome || "").split(" ").map(x => x[0]).slice(0, 2).join(""))}</span>`}</div>
        <div class="ent-txt"><span class="ent-area">${esc(p.area || "")}</span><h3>${esc(p.nome)}</h3>
          <p class="ent-hoje">${esc(p.hoje || "")}</p><p class="ent-stc">${esc(p.funcaoSTC || "")}${p.edicao ? " · " + esc(p.edicao) : ""}</p>
          ${p.citacao ? `<blockquote>“${esc(p.citacao)}”</blockquote>` : ""}
          ${p.link ? `<a class="mini-link" href="${esc(p.link)}" target="_blank" rel="noopener">Ler ou assistir a entrevista ↗</a>` : ""}</div>
      </article>`).join("") + convite;
    $$("[data-video]", ent).forEach(box => box.addEventListener("click", () => {
      $$("video", ent).forEach(v => v.pause());
      box.innerHTML = `<video src="${box.dataset.video}" controls autoplay playsinline preload="auto"></video>`;
    }, { once: true }));
  }

  // Capacitações com fotos
  const caps = $("#caps");
  if (caps) caps.innerHTML = (S.capacitacoes || []).map(c => `<article class="cap reveal">
      ${(c.fotos || []).length ? `<div class="cap-photos">${c.fotos.map(f => `<button class="ph" data-lightbox="${esc(f)}"><img src="${esc(f)}" alt="${esc(c.titulo)}" loading="lazy"></button>`).join("")}</div>` : ""}
      <div class="cap-body"><span class="eyebrow">${esc(c.data || "Capacitação")}</span><h3>${esc(c.titulo)}</h3><div class="who">${esc(c.convidado)}</div>${c.bio ? `<p class="bio">${esc(c.bio)}</p>` : ""}<p>${esc(c.texto)}</p>
      ${c.instagram ? `<a class="mini-link" href="${esc(c.instagram)}" target="_blank" rel="noopener">Ver publicação ↗</a>` : ""}</div>
    </article>`).join("");

  // Carrossel de cards oficiais
  const cards = $("#cards");
  if (cards) { if ((S.cards || []).length) cards.innerHTML = S.cards.map(f => `<button class="card-slide" data-lightbox="${esc(f)}"><img src="${esc(f)}" alt="" loading="lazy"></button>`).join(""); else cards.closest("section")?.remove(); }
  $$("[data-scroll]").forEach(b => b.addEventListener("click", () => { const t = $(b.dataset.target); t && t.scrollBy({ left: (+b.dataset.scroll) * t.clientWidth * 0.8, behavior: "smooth" }); }));

  const sel = $("#selected");
  if (sel) sel.innerHTML = (S.selecionados || []).length ? S.selecionados.map(s => `<div class="reveal"><b>${esc(s.nome)}</b><span>${esc(s.funcao)}</span></div>`).join("")
    : `<p class="empty">A lista completa foi divulgada no Instagram${S.selecionadosInstagram ? ` — <a href="${esc(S.selecionadosInstagram)}" target="_blank" rel="noopener" style="text-decoration:underline">ver publicação ↗</a>` : ""}.</p>`;

  // Lightbox
  document.addEventListener("click", e => {
    const t = e.target.closest("[data-lightbox]"); if (!t) return;
    const lb = document.createElement("div"); lb.className = "lightbox";
    lb.innerHTML = `<img src="${esc(t.dataset.lightbox)}" alt=""><button aria-label="Fechar">×</button>`;
    lb.addEventListener("click", () => lb.remove()); document.body.appendChild(lb);
  });
  const gal = $("#gallery");
  if (gal) { if ((S.fotos || []).length) gal.innerHTML = S.fotos.map(f => `<img src="${esc(f)}" alt="" loading="lazy">`).join(""); else gal.closest("section")?.remove(); }

  /* ---------- Revelar ao rolar ---------- */
  function observe(root = document) { $$(".reveal:not(.in)", root).forEach((el, i) => { el.style.transitionDelay = (i % 6) * 0.06 + "s"; io ? io.observe(el) : el.classList.add("in"); }); }
  observe();

  const y = $("#year"); if (y) y.textContent = new Date().getFullYear();
})();

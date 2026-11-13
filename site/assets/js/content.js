/* =====================================================================
   LATS UFRN — CONTEÚDO DO SITE
   ---------------------------------------------------------------------
   Este é o ÚNICO arquivo que vocês precisam editar no dia a dia.
   Para adicionar um membro, artigo, vídeo, podcast ou formulário,
   copie um bloco { ... } existente, cole logo abaixo e troque os textos.
   Itens marcados com "EXEMPLO" são modelos: substituam pelos reais.
   ===================================================================== */

window.LATS = {

  /* ---------- Redes e contato ---------- */
  redes: {
    instagram: "https://www.instagram.com/latsufrn/",
    instagramUser: "@latsufrn",
    linkedin: "https://www.linkedin.com/company/latsufrn/",  // confirmar URL
    linktree: "https://linktr.ee/latsufrn",
    youtube: "",          // ex.: "https://www.youtube.com/@latsufrn"
    spotify: "",          // ex.: link do podcast no Spotify
    email: "latsufrn@gmail.com"  // confirmar e-mail
  },

  /* ---------- Feed automático do Instagram ----------
     Para o site se atualizar sozinho com os posts do Instagram:
     1. Crie uma conta grátis em https://behold.so e conecte o @latsufrn
     2. Crie um "feed" do tipo Widget e copie o "Feed ID"
     3. Cole abaixo em beholdFeedId.
     Enquanto estiver vazio, o site mostra os posts listados em "postsFixos". */
  instagramFeed: {
    beholdFeedId: "",
    postsFixos: [
      // Cole aqui links de posts que quiser destacar, ex.:
      // "https://www.instagram.com/p/CODIGO_DO_POST/"
    ]
  },

  /* ---------- LinkedIn ----------
     No LinkedIn, abra um post > "..." > "Incorporar este post" > copie o
     endereço que está dentro de src="..." e cole aqui. */
  linkedinPosts: [
    // "https://www.linkedin.com/embed/feed/update/urn:li:share:0000000000000000000"
  ],

  /* ---------- Em julgamento: destaques da equipe ----------
     O painel "Em julgamento" é preenchido automaticamente pelo robô.
     Para fixar um caso no topo, com relator e placar conferidos pela equipe,
     copie o modelo abaixo (tribunal: "STF" ou "STJ"):
     { tribunal: "STF", tema: "Tema do caso", processo: "ADI 0000", relator: "Min. Nome",
       placar: "5 x 2", status: "Em julgamento", link: "https://...", data: "2026-11-12" } */
  emJulgamentoDestaques: [],

  /* ---------- Números da home ---------- */
  numeros: [
    { valor: "XVIII", rotulo: "edições da Simulação de Tribunais Constitucionais" },
    { valor: "1.6k+", rotulo: "seguidores no Instagram" },
    { valor: "2",     rotulo: "Tribunais Superiores em foco: STF e STJ" }
  ],

  /* ---------- Membros ----------
     A ordem aqui é a ordem no site: Coordenação Geral primeiro,
     depois as demais coordenações em ordem alfabética do cargo.
     grupo: "Fundadores" (pode criar outros, ex.: "Membros 2027", "Orientação")
     foto: caminho da imagem em assets/img/membros/ (proporção 4:5) */
  fotoGrupo: { foto: "assets/img/membros/fundadores-grupo.jpg", legenda: "Membros fundadores da LATS UFRN" },

  membros: [
    { nome: "Camila Silveira",           cargo: "Coordenadora Geral",               grupo: "Fundadores", foto: "assets/img/membros/camila-silveira.jpg",           linkedin: "", lattes: "" },
    { nome: "Vítor Heronildes",          cargo: "Coordenador Geral",                grupo: "Fundadores", foto: "assets/img/membros/vitor-heronildes.jpg",          linkedin: "", lattes: "" },
    { nome: "Hutay Tizziani",            cargo: "Coordenador de Extensão",          grupo: "Fundadores", foto: "assets/img/membros/hutay-tizziani.jpg",            linkedin: "" },
    { nome: "Renato Dias",               cargo: "Coordenador de Extensão",          grupo: "Fundadores", foto: "assets/img/membros/renato-dias.jpg",               linkedin: "" },
    { nome: "Ana Júlia Lauar",           cargo: "Coordenadora de Marketing",        grupo: "Fundadores", foto: "assets/img/membros/ana-julia-lauar.jpg",           linkedin: "" },
    { nome: "André Henrique",            cargo: "Coordenador de Parcerias",         grupo: "Fundadores", foto: "assets/img/membros/andre-henrique.jpg",            linkedin: "" },
    { nome: "Samuel Cavalcanti",         cargo: "Coordenador de Parcerias",         grupo: "Fundadores", foto: "assets/img/membros/samuel-cavalcanti.jpg",         linkedin: "" },
    { nome: "Maíra França",              cargo: "Coordenadora de Pesquisa",         grupo: "Fundadores", foto: "assets/img/membros/maira-franca.jpg",              linkedin: "" },
    { nome: "Maria Augusta Von Sohsten", cargo: "Coordenadora de Recursos Humanos", grupo: "Fundadores", foto: "assets/img/membros/maria-augusta-von-sohsten.jpg", linkedin: "" }
  ],

  /* ---------- Artigos e publicações ----------
     tipo: "Artigo", "Informativo", "Resenha", "Nota técnica", "Livro" ...
     tribunal: "STF", "STJ" ou "STF · STJ"
     link: PDF (coloque em assets/docs/) ou link externo */
  publicacoes: [
    { tipo: "Capítulo de livro", tribunal: "STF", data: "2026",
      titulo: "Reflexões acerca da escolha dos Ministros do Supremo Tribunal Federal e sobre o baixo prestígio à carreira da magistratura em sua composição",
      autores: "Vítor Augusto Monteiro Heronildes · Igor Freitas Perdigão",
      membro: "Vítor Augusto Monteiro Heronildes, Coordenador Geral da LATS",
      orientacao: "Prof. Dr. Ricardo Tinôco de Góes (UFRN · ESMARN), Juiz de Direito",
      publicadoEm: "Dilemas do ordenamento jurídico em perspectiva: dos fundamentos teóricos à aplicação do direito. Editora Noeses, pp. 337–367.",
      palavras: ["Composição do STF", "Art. 101 da CF", "Magistratura de carreira", "Indicação presidencial", "Sabatina no Senado"],
      resumo: "Até que ponto os requisitos do art. 101 da Constituição — notável saber jurídico e reputação ilibada — abrem espaço para indicações que deixam de fora a magistratura de carreira? O capítulo analisa a composição histórica do STF, o papel homologatório do Senado e a presença de um único juiz de carreira na Corte atual, e discute propostas de reforma à luz de modelos estrangeiros, como a densificação dos requisitos, a quarentena para ocupantes de cargos políticos e a reserva de vagas à magistratura.",
      link: "artigos/escolha-ministros-stf-magistratura.html",
      pdf: "assets/docs/escolha-ministros-stf-magistratura.pdf" }
    /* Para adicionar outro trabalho, copie o bloco acima. Campos opcionais:
       membro (vínculo do autor com a LATS), orientacao, publicadoEm, palavras. */
  ],

  /* =================================================================
     VÍDEOS — PODCAST e AULAS GRAVADAS
     -----------------------------------------------------------------
     No campo "video" você pode colar QUALQUER um destes:
       • link do YouTube  (https://www.youtube.com/watch?v=XXXX ou https://youtu.be/XXXX)
       • link do Google Drive (arquivo compartilhado como "qualquer pessoa com o link")
       • link do Spotify (episódio) — vira um player de áudio
       • arquivo de vídeo colocado na pasta assets/videos/ (ex.: "assets/videos/aula1.mp4")
       • link do Instagram (Reels/post) — vira um botão "Assistir no Instagram"
     Deixe "video" vazio para mostrar o card como "em breve".
     O primeiro item de cada lista é o destaque (aparece no player grande).
     ================================================================= */
  podcast: [
    { episodio: "EP 01", titulo: "EXEMPLO — Quem fiscaliza o guardião da Constituição?", convidados: "Convidado(a) a definir", data: "", duracao: "", descricao: "Primeiro episódio do podcast da LATS: os limites institucionais do STF e os projetos de reforma do Supremo.", video: "" },
    { episodio: "EP 02", titulo: "EXEMPLO — Bastidores de uma sustentação oral", convidados: "Convidado(a) a definir", data: "", duracao: "", descricao: "Como se prepara uma sustentação oral perante os Tribunais Superiores.", video: "" },
    { episodio: "EP 03", titulo: "EXEMPLO — Precedentes no STJ: o que muda na prática?", convidados: "Convidado(a) a definir", data: "", duracao: "", descricao: "Recursos repetitivos, IRDR e a força dos precedentes qualificados.", video: "" }
  ],

  aulas: [
    { categoria: "Aula Inaugural", titulo: "Quis custodiet ipsos custodes? O Modelo de 1988, a Restauração dos Limites Institucionais e os Projetos de Reforma do Supremo", palestrantes: "Profa. Dra. Christine Peter · Profa. Dra. Ana Beatriz Presgrave · Prof. Dr. Pedro de Oliveira Alves", data: "", descricao: "Aula Inaugural da LATS, realizada na Assembleia Legislativa do RN.", video: "", instagram: "https://www.instagram.com/p/Dd_uB0CNJrL/" },
    { categoria: "Capacitação STC", titulo: "Capacitação da AGU — XVIII Simulação de Tribunais Constitucionais", palestrantes: "Prof. Dr. Cláudio Seefelder", data: "2026-11-10", descricao: "Encontro remoto de preparação dos participantes da Advocacia-Geral da União.", video: "", capa: "assets/img/stc/agu-1-foto.jpg", instagram: "https://www.instagram.com/p/DfmwNsYFfGJ/" },
    { categoria: "Capacitação STC", titulo: "Capacitação dos Advogados do Requerente — XVIII STC", palestrantes: "Dr. Jules Queiroz", data: "2026-10-29", descricao: "Primeira capacitação da edição, voltada aos advogados do requerente.", video: "", capa: "assets/img/stc/req-1-foto.jpg", instagram: "https://www.instagram.com/p/DfIIW-lFG7h/" },
    { categoria: "Aula", titulo: "EXEMPLO — Introdução ao controle concentrado de constitucionalidade", palestrantes: "Nome do(a) professor(a)", data: "", descricao: "Aula do ciclo de formação interna da Liga.", video: "" }
  ],

  /* ---------- Inscrições e formulários ----------
     status: "aberto", "em breve" ou "encerrado"
     link: link do Google Forms (ou outro)
     tema: "liga" (azul) ou "stc" (verde) */
  formularios: [
    { titulo: "Processo Seletivo LATS", descricao: "Seleção de novos membros para pesquisa, ensino e extensão.", status: "em breve", prazo: "", link: "", tema: "liga" },
    { titulo: "XVIII Simulação de Tribunais Constitucionais", descricao: "Inscrições para a nova edição da STC.", status: "encerrado", prazo: "", link: "stc.html", tema: "stc" },
    { titulo: "Envio de artigos", descricao: "Submeta seu artigo para publicação nos canais da Liga.", status: "aberto", prazo: "Fluxo contínuo", link: "", tema: "liga" },
    { titulo: "Lista de interesse / Newsletter", descricao: "Receba avisos de eventos, aulas e seleções.", status: "aberto", prazo: "", link: "", tema: "liga" }
  ],

  /* ---------- Links úteis ---------- */
  links: [
    { titulo: "Supremo Tribunal Federal", url: "https://portal.stf.jus.br/" },
    { titulo: "Superior Tribunal de Justiça", url: "https://www.stj.jus.br/" },
    { titulo: "Informativos do STF", url: "https://portal.stf.jus.br/textos/verTexto.asp?servico=informativoSTF" },
    { titulo: "Informativos do STJ", url: "https://processo.stj.jus.br/jurisprudencia/externo/informativo/" },
    { titulo: "Pauta do Plenário do STF", url: "https://portal.stf.jus.br/pauta/" },
    { titulo: "UFRN", url: "https://www.ufrn.br/" }
  ],

  /* =================================================================
     STC — SIMULAÇÃO DE TRIBUNAIS CONSTITUCIONAIS (página verde)
     ================================================================= */
  stc: {
    edicao: "XVIII",
    titulo: "Simulação de Tribunais Constitucionais",
    chamada: "A bancada está pronta. O caso está posto. Só falta você na tribuna.",
    dataSessao: "27 de novembro de 2026",
    inscricaoLink: "https://linktr.ee/latsufrn",  // troque pelo link direto do formulário
    editalLink: "https://linktr.ee/latsufrn",     // PDF do edital (ex.: "assets/docs/edital-stc.pdf")
    casoLink: "",                                 // PDF do caso concreto

    caso: {
      titulo: "ADI nº 9.001",
      tema: "Cancelamento automático de benefício social de quem aposta em plataformas on-line (ADI nº 9.001, lei fictícia)",
      texto: "A edição de 2026 tem por objeto a Ação Direta de Inconstitucionalidade nº 9.001, ajuizada contra uma lei fictícia que institui o cancelamento automático de benefício social de titulares que realizem apostas em plataformas on-line. Cabe ao Supremo Tribunal Federal decidir se a norma é compatível com a Constituição Federal de 1988."
    },

    /* História da STC — linha do tempo */
    historia: [
      { ano: "Origem", titulo: "Uma tradição do Curso de Direito da UFRN", texto: "A Simulação de Tribunais Constitucionais reproduz um julgamento perante o Supremo Tribunal Federal e se consolidou como uma das atividades acadêmicas mais tradicionais do Curso de Direito da UFRN, marcando gerações de estudantes." },
      { ano: "Até 2021", titulo: "Dezessete edições", texto: "Ao longo de dezessete edições, com sessões no Pleno do TJRN e parcerias com a Justiça Federal, estudantes ocuparam a bancada e a tribuna de um Plenário simulado. Em 2020, durante a pandemia, a STC promoveu uma série de lives sobre a Constituição." },
      { ano: "2026", titulo: "Nasce a LATS", texto: "A Liga Acadêmica de Tribunais Superiores da UFRN é lançada como herdeira do legado da STC, retomando essa trajetória com escopo ampliado: ensino, pesquisa e extensão." },
      { ano: "2026", titulo: "XVIII edição — a tradição retomada", texto: "A Simulação volta sob a organização da LATS, com processo seletivo, capacitações com profissionais que atuam nas Cortes e sessão de julgamento em 27 de novembro." }
    ],
    /* ---------- Acervo das edições anteriores ----------
       Fotos e informações tiradas do Instagram da STC (@latsufrn, antigo perfil da Simulação).
       Para incluir outra edição (ex.: XVI, XVII), copie um bloco e preencha.
       Hall da STC: "decisao" = resultado do Plenário; "destaques" = premiados, ex.:
         destaques: [{ premio: "Melhor orador(a)", nome: "Nome Sobrenome" }, { premio: "Equipe vencedora", nome: "AGU" }] */
    edicoes: [
      { numero: "XV", ano: "2019", tema: "Suspensão temporária de aplicativos de mensagens por decisão judicial",
        texto: "Uma ADI impugnou dispositivos do Marco Civil da Internet (Lei nº 12.965/2014) que permitiam suspender aplicativos de mensagens como punição pelo descumprimento de ordens judiciais. O Plenário decidiu pela constitucionalidade dos dispositivos. O ciclo foi aberto em parceria com a Justiça Federal no RN, dentro da Quinta Jurídica.",
        fotos: ["assets/img/stc/historia/xv-1.jpg", "assets/img/stc/historia/xv-2.jpg", "assets/img/stc/historia/xv-3.jpg", "assets/img/stc/historia/xv-4.jpg"],
        decisao: "Constitucionalidade dos dispositivos questionados", destaques: [],
        credito: "", instagram: "https://www.instagram.com/p/CAd00m4F73d/" },
      { numero: "XIV", ano: "2018", tema: "A (in)constitucionalidade da proibição da candidatura avulsa",
        texto: "A abertura ocorreu em parceria com a Justiça Federal, nos moldes da Quinta Jurídica, com a Profa. Dra. Ana Beatriz Presgrave e a Procuradora Regional Eleitoral do RN, Dra. Cibele Benevides. Na sessão, a AGU, o requerente e o Ministério Público Federal sustentaram suas posições perante os Ministros.",
        fotos: ["assets/img/stc/historia/xiv-1.jpg", "assets/img/stc/historia/xiv-2.jpg", "assets/img/stc/historia/xiv-3.jpg", "assets/img/stc/historia/xiv-4.jpg", "assets/img/stc/historia/xiv-5.jpg"],
        decisao: "", destaques: [],
        credito: "", instagram: "https://www.instagram.com/p/BqL0IuSFAZr/" },
      { numero: "XIII", ano: "2017", tema: "Os limites constitucionais dos acordos de colaboração premiada",
        texto: "Realizada em 27 de outubro, no Pleno do Tribunal de Justiça do Rio Grande do Norte. A abertura foi feita em parceria com o Projeto Quinta Jurídica.",
        fotos: ["assets/img/stc/historia/xiii-1.jpg", "assets/img/stc/historia/xiii-5.jpg", "assets/img/stc/historia/xiii-2.jpg", "assets/img/stc/historia/xiii-3.jpg", "assets/img/stc/historia/xiii-4.jpg"],
        decisao: "", destaques: [],
        credito: "Fotos: Augusto César Bezerra", instagram: "https://www.instagram.com/p/Ba4uL0DDe9y/" },
      { numero: "XII", ano: "2016", tema: "Regulamentação do ensino domiciliar no Brasil",
        texto: "Realizada em 14 de outubro de 2016, no Pleno do Tribunal de Justiça do Rio Grande do Norte, com registro da TV Ponta Negra.",
        fotos: ["assets/img/stc/historia/xii-4.jpg", "assets/img/stc/historia/xii-3.jpg", "assets/img/stc/historia/xii-1.jpg"],
        decisao: "", destaques: [],
        credito: "Fotos: Augusto César Bezerra", instagram: "https://www.instagram.com/p/BLmUrKwF0YW/" },
      { numero: "XI", ano: "2015", tema: "O Novo Código de Processo Civil",
        texto: "Os Ministros debateram a constitucionalidade de dispositivos do Novo CPC, como a ordem cronológica de julgamentos e a sucumbência recursal com honorários advocatícios.",
        fotos: ["assets/img/stc/historia/xi-1.jpg", "assets/img/stc/historia/xi-4.jpg", "assets/img/stc/historia/xi-3.jpg"],
        decisao: "", destaques: [],
        credito: "Fotos: Augusto Bezerra e Vinicius Damasceno", instagram: "https://www.instagram.com/p/9PTnB-FCVC/" },
      { numero: "X", ano: "2014", tema: "O direito à saúde na Constituição de 1988",
        texto: "Edição comemorativa de 10 anos da Simulação, com a participação de representantes do Conselho Federal de Medicina, do Conselho Nacional de Saúde e do Sindsaúde-SP.",
        fotos: ["assets/img/stc/historia/x-2.jpg", "assets/img/stc/historia/x-1.jpg", "assets/img/stc/historia/x-3.jpg"],
        decisao: "", destaques: [],
        credito: "", instagram: "https://www.instagram.com/p/tIu7t8lCY1/" }
    ],

    papeis: [
      { titulo: "Ministros", vagas: "10 vagas", texto: "Ouvem todas as posições e decidem o caso. Julgam a ação e proferem os votos; um deles atua como Relator. A Presidência do Plenário é exercida pela organização." },
      { titulo: "Advogados do Requerente", vagas: "4 vagas", texto: "Representam o autor da ação, elaboram a peça escrita e sustentam a inconstitucionalidade da lei impugnada." },
      { titulo: "Advocacia-Geral da União", vagas: "4 vagas", texto: "Defende a validade da norma impugnada, nos termos do art. 103, § 3º, da Constituição, por manifestação escrita e sustentação oral." },
      { titulo: "Procuradoria-Geral da República", vagas: "4 vagas", texto: "Não representa nenhuma das partes: atua como fiscal da ordem jurídica e emite parecer sobre a constitucionalidade da lei." }
    ],
    funcionamento: "A Simulação divide-se em duas fases. Na fase escrita, cada litigante elabora sua peça processual. Na Sessão de Julgamento, realizam-se as sustentações orais, os Ministros proferem seus votos e o resultado é proclamado pelo Plenário.",

    cronograma: [
      { data: "até 24/10", titulo: "Inscrições", texto: "Edital publicado e inscrições abertas para Ministros, Requerente, AGU e PGR." },
      { data: "27/10", titulo: "Selecionados", texto: "Divulgação dos acadêmicos selecionados para a equipe de participantes." },
      { data: "29/10", titulo: "Capacitação — Advogados do Requerente", texto: "Com o Dr. Jules Queiroz, Advogado-Geral da Câmara dos Deputados." },
      { data: "10/11", titulo: "Capacitação — AGU", texto: "Com o Prof. Dr. Cláudio Seefelder, Adjunto do Advogado-Geral da União." },
      { data: "27/11", titulo: "Sessão de Julgamento", texto: "Sustentações orais, votos dos Ministros e proclamação do resultado pelo Plenário." }
    ],

    capacitacoes: [
      { titulo: "Capacitação da AGU", data: "10 de novembro de 2026", convidado: "Prof. Dr. Cláudio Seefelder", bio: "Adjunto do Advogado-Geral da União, Mestre em Direito Tributário e Desenvolvimento Econômico pelo IDP e professor nas pós-graduações de Direito Tributário do IDP e da Faculdade Presbiteriana Mackenzie Rio.", texto: "Em formato remoto e voltada aos participantes da Advocacia-Geral da União, a capacitação contribuiu para a preparação dos debates e a construção das teses.", fotos: ["assets/img/stc/agu-1-foto.jpg", "assets/img/stc/agu-2-foto.jpg"], instagram: "https://www.instagram.com/p/DfmwNsYFfGJ/" },
      { titulo: "Capacitação dos Advogados do Requerente", data: "29 de outubro de 2026", convidado: "Dr. Jules Queiroz", bio: "Advogado-Geral da Câmara dos Deputados, Mestre pela UnB e Doutor em Direito pela USP.", texto: "Primeira capacitação da edição, em formato remoto e voltada aos advogados do requerente, com dúvidas respondidas e debates sobre a construção das teses.", fotos: ["assets/img/stc/req-1-foto.jpg", "assets/img/stc/req-2-foto.jpg"], instagram: "https://www.instagram.com/p/DfIIW-lFG7h/" }
    ],

    /* Cards oficiais publicados no Instagram (aparecem num carrossel) */
    cards: [
      "assets/img/stc/card-ed-1.jpg", "assets/img/stc/card-ed-2.jpg", "assets/img/stc/card-ed-3.jpg",
      "assets/img/stc/card-ed-4.jpg", "assets/img/stc/card-ed-5.jpg", "assets/img/stc/card-ed-6.jpg",
      "assets/img/stc/card-ed-7.jpg"
    ],

    /* ---------- Entrevistas: onde estão hoje os ex-participantes ----------
       Modelo:
       { nome: "Nome Sobrenome", foto: "assets/img/stc/entrevistas/nome.jpg",
         edicao: "XIII STC · 2017", funcaoSTC: "Ministra relatora",
         hoje: "Juíza federal no TRF5", area: "Magistratura",   // Magistratura, Advocacia, Academia, Ministério Público, Advocacia Pública...
         citacao: "Uma frase marcante da entrevista.",
         video: "assets/videos/nome.mp4", capa: "assets/videos/nome.jpg",  // depoimento em vídeo (opcional)
         link: "" }   // ou link externo: YouTube, podcast, texto completo */
    entrevistas: [
      { nome: "Jules Queiroz", video: "assets/videos/jules-queiroz.mp4", capa: "assets/videos/jules-queiroz.jpg",
        edicao: "", funcaoSTC: "Na STC: Amicus curiae, AGU e Ministro",
        hoje: "Advogado-Geral da Câmara dos Deputados", area: "Advocacia Pública",
        citacao: "", link: "" },
      { nome: "Rachel Tinôco", video: "assets/videos/rachel-tinoco.mp4", capa: "assets/videos/rachel-tinoco.jpg",
        edicao: "", funcaoSTC: "Na STC: AGU e Ministra",
        hoje: "Juíza Federal no TRF da 3ª Região", area: "Magistratura",
        citacao: "", link: "" }
    ],
    entrevistasConvite: "https://www.instagram.com/latsufrn/",   // formulário para ex-participantes contarem sua história

    selecionados: [
      // { nome: "Nome Sobrenome", funcao: "Ministro(a)" },
    ],
    selecionadosInstagram: "https://www.instagram.com/p/DfAIS2OlO4I/",
    fotos: []
  }
};

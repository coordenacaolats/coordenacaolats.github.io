# Site da LATS UFRN

Site estático, sem mensalidade e sem banco de dados. Tem duas páginas:

- `index.html` é a página da Liga, toda em **azul**.
- `stc.html` é a página da Simulação de Tribunais Constitucionais, toda em **verde**.

## 1. Como atualizar o conteúdo

Tudo fica em **`assets/js/content.js`**. É lá que vocês adicionam membros, artigos, vídeos, podcasts, formulários e links, e mudam as informações da STC.
Para adicionar um item, copiem um bloco `{ ... }` que já existe, colem logo abaixo e troquem os textos. Os itens marcados com "EXEMPLO" são só modelos.

| O que | Onde em `content.js` | Observações |
|---|---|---|
| Membros | `membros` | Fotos ficam em `assets/img/membros/`. Sem foto, o site mostra as iniciais. |
| Artigos e PDFs | `publicacoes` | Os PDFs ficam em `assets/docs/`, e o `link` aponta para `assets/docs/arquivo.pdf`. |
| Podcast (vídeo ou áudio) | `podcast` | No campo `video`, cole o link do YouTube, do Google Drive, do Spotify ou de um `.mp4`. O primeiro episódio da lista aparece no player grande. |
| Aulas e eventos gravados | `aulas` | Use o mesmo campo `video`. Sem vídeo, o card aparece como "Gravação em breve". `categoria` vira o filtro. |
| Fotos das STCs antigas | `stc.fotosHistoria` | Coloquem as fotos em `assets/img/stc/historia/` e escrevam `{ foto: "assets/img/stc/historia/2019.jpg", legenda: "XVI edição, 2019" }`. |
| Inscrições | `formularios` | `status` pode ser `aberto`, `em breve` ou `encerrado`. `tema: "stc"` deixa o card verde. |
| STC | `stc` | Links de inscrição, edital e caso, cronograma, capacitações, selecionados e fotos. |

## 2. Instagram com atualização automática

1. Criem uma conta grátis em **behold.so** e conectem o @latsufrn.
2. Criem um feed do tipo "Widget" e copiem o **Feed ID**.
3. Colem o ID em `instagramFeed.beholdFeedId` no `content.js`.

Depois disso, cada post novo no Instagram aparece no site sozinho.
Enquanto não houver um ID, o site mostra os posts colados em `postsFixos`. Se essa lista também estiver vazia, aparece um mosaico com o símbolo da Liga.

## 3. LinkedIn

O LinkedIn não oferece um feed automático gratuito para páginas. Há dois caminhos:

- **Grátis:** em cada post, abram "..." e depois "Incorporar este post". Copiem o endereço que está em `src="..."` e colem em `linkedinPosts`.
- **Automático (pago):** usar um widget como Elfsight ou SociableKIT e colar o código do widget no bloco `#li-feed` do `index.html`.

## 4. Publicar o site (grátis)

- **Netlify:** acessem app.netlify.com/drop e arrastem a pasta `site` para a página.
- **GitHub Pages:** subam a pasta para um repositório e ativem o Pages em Settings.

Depois disso, dá para apontar um domínio próprio, como `lats.ufrn.br` ou `latsufrn.com.br`.

## 5. Ver no computador

Rodem `python3 -m http.server 8123` dentro desta pasta e abram http://localhost:8123.

## 6. Informativo, Em julgamento e notícias automáticas

**Como funciona**
- O robô `scripts/atualizar_tribunais.py` lê as notícias oficiais de **stf.jus.br** e **stj.jus.br**. A leitura passa pelo Google Notícias, porque os portais dos tribunais bloqueiam acesso automatizado.
- O robô classifica cada notícia em decisão, pauta, nova ação ou institucional e monta o painel **Em julgamento**.
- Duas vezes por dia, às 6h e às 18h, o GitHub atualiza `site/data/tribunais.js` e republica o site. O fluxo que faz isso está em `.github/workflows/publicar.yml`.
- **Informativo LATS:** toda segunda-feira, às 8h, o Claude redige a edição da semana e abre um *Pull Request*. Alguém da Liga lê, corrige se precisar e clica em **Merge**, e a edição vai para o site. O fluxo está em `.github/workflows/informativo-semanal.yml`.
- **Sem a chave da IA:** o site continua funcionando. O painel mostra as notícias de pauta sem relator e placar, e o Informativo mostra um "resumo automático da semana" com as manchetes de decisões.

**Para ligar (uma vez só)**
1. Crie um repositório no GitHub e envie esta pasta inteira (inclusive `.github` e `scripts`).
2. Em **Settings › Pages**, escolha *Source: GitHub Actions*.
3. Em **Settings › Actions › General**, marque *Read and write permissions* e *Allow GitHub Actions to create and approve pull requests*.
4. Para a IA, crie uma chave em console.anthropic.com e cadastre-a em **Settings › Secrets and variables › Actions** com o nome `ANTHROPIC_API_KEY`. Custa alguns centavos de dólar por semana.
5. Em **Actions**, rode "Atualizar e publicar site" manualmente uma vez para testar.

**Fixar um caso no painel:** use `emJulgamentoDestaques` no `content.js`, com relator e placar conferidos pela equipe.

## 7. Glossário, Hall da STC e Entrevistas
- **Glossário:** os verbetes ficam em `site/data/glossario.js`. Copie um bloco e preencha. A ordem alfabética, a busca e os links "veja também" são automáticos.
- **Hall da STC:** em `stc.edicoes`, preencha `decisao` (resultado do Plenário) e `destaques` (premiados) de cada edição. Para a edição atual, use `stc.decisaoAtual` e `stc.destaquesAtuais`.
- **Entrevistas:** em `stc.entrevistas`, siga o modelo comentado. Enquanto a lista estiver vazia, aparece um convite para ex-participantes. O link do convite fica em `entrevistasConvite`.

Para atualizar as notícias no seu computador, rode:

    python3 scripts/atualizar_tribunais.py

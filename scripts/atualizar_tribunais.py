#!/usr/bin/env python3
"""
LATS UFRN — coletor automático de notícias do STF e do STJ.

O que faz:
  1. Lê as notícias oficiais publicadas em stf.jus.br e stj.jus.br
     (via RSS do Google Notícias, porque os portais dos tribunais bloqueiam robôs).
  2. Classifica cada notícia (decisão, pauta/julgamento, institucional).
  3. Monta o painel "Em julgamento".
  4. (Opcional, com ANTHROPIC_API_KEY) usa o Claude para preencher as fichas
     do painel e, com --informativo, redigir a edição semanal do Informativo LATS.
  5. Grava tudo em site/data/tribunais.js, que o site lê.

Uso:
  python scripts/atualizar_tribunais.py                 # notícias + painel
  python scripts/atualizar_tribunais.py --informativo   # + nova edição do Informativo (precisa da chave)

Sem dependências externas, exceto o pacote `anthropic` na etapa opcional de IA.
"""
from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import html
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "site" / "data" / "tribunais.js"            # notícias + painel (atualização diária)
PREFIXO = "window.LATS_TRIBUNAIS = "
SAIDA_INFO = RAIZ / "site" / "data" / "informativos.js"    # edições do Informativo (revisadas por PR)
PREFIXO_INFO = "window.LATS_INFORMATIVOS = "

# consulta no Google Notícias + endereço de origem aceito (descarta páginas de processo, agenda etc.)
FONTES = {
    "STF": ("site:stf.jus.br", "noticias.stf.jus.br"),
    "STJ": ("site:stj.jus.br", "www.stj.jus.br"),
}
RE_AGENDA = re.compile(
    r"^(sess[ãa]o( do| de| plen)|palestra|aula|confer[êe]ncia|reuni[ãa]o|audi[êe]ncia com|visita|entrevista|"
    r"participa[çc][ãa]o|abertura do|encerramento|lan[çc]amento do livro|solenidade|tema \d+|dra?\.\s)|assunto:", re.I)
DIAS = 14              # janela de notícias
MAX_POR_TRIBUNAL = 40
MAX_EDICOES = 26       # meio ano de informativos guardados
MODELO = "claude-opus-5-5"
USER_AGENT = "LATS-UFRN-site/1.0 (+https://www.instagram.com/latsufrn/)"

RE_PAUTA = re.compile(
    r"\bpauta\b|julgamento|plen[áa]rio|\bvota\b|\bvoto\b|relator[a]? |pedido de vista|\bvista\b|"
    r"maioria|placar|retoma|come[çc]a a julgar|vai (definir|julgar|decidir|analisar)|"
    r"sess[ãa]o|audi[êe]ncia p[úu]blica|repercuss[ãa]o geral|repetitivo|afeta", re.I)
RE_DECISAO = re.compile(
    r"\b(decide|mant[ée]m|invalida|derruba|valida|afasta|reconhece|garante|nega|rejeita|confirma|"
    r"determina|fixa|declara|anula|suspende|restabelece|condena|absolve|aumenta|reduz|autoriza|"
    r"permite|pro[íi]be|impede|assegura|define|considera|entende|admite|veda)\b", re.I)
RE_INSTITUCIONAL = re.compile(
    r"\b(ouvidoria|selo|programa|lan[çc]a|visita|reuni[ãa]o|re[úu]ne|concurso|est[áa]gio|servidor(es)?|"
    r"posse|homenage|semin[áa]rio|curso|evento|parceria|acordo de coopera[çc][ãa]o|portal|podcast|"
    r"stj not[íi]cias destaca|r[áa]dio|tv justi[çc]a|biblioteca|museu|transpar[êe]ncia|encontro|f[óo]rum|"
    r"confer[êe]ncia|livro|obra|tutorial|contratos?|v[íi]deo|enfam|ju[íi]zas?|moot|congresso|homenageado|"
    r"cumprimenta|recebe|defende|destaca|pr[êe]mio)\b", re.I)
RE_NOVA_ACAO = re.compile(r"\b(questiona|questionam|aciona|acionam|aju[íi]za|contesta|contestam|pede(m)? ao (STF|STJ)|vai ao STF)\b", re.I)
RE_PROCESSO = re.compile(
    r"\b(ADI|ADPF|ADC|ADO|RE|ARE|HC|RHC|REsp|AREsp|MS|MI|Rcl|EREsp|IAC|Tema)\)?\s*(n[ºo°.]*\s*)?(\d[\d.]*)", re.I)


# ---------------------------------------------------------------- coleta
def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def limpar_titulo(titulo: str) -> str:
    titulo = html.unescape(titulo or "").strip()
    # o Google Notícias acrescenta " - fonte" ao fim do título
    return re.sub(r"\s+-\s+(stf not[íi]cias|STJ|STF|Superior Tribunal de Justi[çc]a|Supremo Tribunal Federal)\s*$",
                  "", titulo, flags=re.I).strip()


def classificar(titulo: str, tribunal: str) -> str:
    if re.match(r"presidente d[oa] (STF|STJ)", titulo, re.I) or RE_INSTITUCIONAL.search(titulo):
        if not re.search(r"relator[a]? vota|vai (definir|julgar|decidir)", titulo, re.I):
            return "institucional"
    if re.match(r"(STF|STJ|Supremo|Plen[áa]rio|\w+ (Turma|Se[çc][ãa]o))\s", titulo) and RE_DECISAO.search(" ".join(titulo.split()[:3])):
        return "decisao"
    if RE_NOVA_ACAO.search(titulo):
        return "nova_acao"
    if re.search(r"vai (definir|julgar|decidir|analisar)|come[çc]a a julgar|retoma|pauta|pedido de vista|"
                 r"relator[a]? vota|placar|maioria", titulo, re.I):
        return "pauta"
    if RE_DECISAO.search(titulo):
        return "decisao"
    if RE_PAUTA.search(titulo):
        return "pauta"
    # as notícias jurídicas do STJ costumam anunciar a tese sem um verbo de decisão
    return "decisao" if tribunal == "STJ" else "outros"


SIGLAS = {"resp": "REsp", "aresp": "AREsp", "eresp": "EREsp", "rcl": "Rcl", "tema": "Tema"}


def formatar_processo(m: re.Match | None) -> str:
    if not m:
        return ""
    sigla = SIGLAS.get(m.group(1).lower(), m.group(1).upper())
    return f"{sigla} {m.group(3).rstrip('.')}"


def coletar(tribunal: str, consulta: str, origem: str) -> list[dict]:
    q = urllib.parse.quote(f"{consulta} when:{DIAS}d")
    url = f"https://news.google.com/rss/search?q={q}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    raiz = ET.fromstring(baixar(url))
    itens = []
    for it in raiz.iter("item"):
        titulo = limpar_titulo(it.findtext("title"))
        fonte = it.find("source")
        if fonte is None or origem not in (fonte.get("url") or ""):
            continue
        if not titulo or len(titulo.split()) < 5 or RE_AGENDA.search(titulo):
            continue
        try:
            data = email.utils.parsedate_to_datetime(it.findtext("pubDate")).astimezone(dt.timezone.utc)
        except (TypeError, ValueError):
            continue
        proc = RE_PROCESSO.search(titulo)
        itens.append({
            "tribunal": tribunal,
            "titulo": titulo,
            "link": it.findtext("link") or "",
            "data": data.isoformat(timespec="minutes"),
            "tipo": classificar(titulo, tribunal),
            "processo": formatar_processo(proc),
        })
    # remove duplicatas (mesmo título) e ordena do mais recente para o mais antigo
    vistos, unicos = set(), []
    for i in sorted(itens, key=lambda x: x["data"], reverse=True):
        chave = re.sub(r"\W+", "", i["titulo"].lower())[:80]
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(i)
    return unicos[:MAX_POR_TRIBUNAL]


def candidatas_painel(noticias: list[dict]) -> list[dict]:
    return [n for n in noticias
            if n["tipo"] == "pauta" and not re.search(r"confira a pauta|destaques da pauta", n["titulo"], re.I)]


# ---------------------------------------------------------------- texto completo das notícias
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def texto_stf(titulo: str) -> tuple[str, str] | None:
    """Busca a notícia na interface pública do portal de notícias do STF (WordPress).
    Devolve (texto, link oficial) ou None."""
    palavras = _norm(titulo)
    termo = urllib.parse.quote(" ".join(palavras[:9]))
    url = (f"https://noticias.stf.jus.br/wp-json/wp/v2/posts?search={termo}&per_page=5"
           f"&_fields=link,title,content")
    try:
        posts = json.loads(baixar(url))
    except Exception:
        return None
    alvo = set(palavras)
    melhor, nota = None, 0.0
    for p in posts:
        t = set(_norm(html.unescape(p["title"]["rendered"])))
        semelhanca = len(alvo & t) / max(1, len(alvo | t))
        if semelhanca > nota:
            melhor, nota = p, semelhanca
    if not melhor or nota < 0.6:
        return None
    texto = html.unescape(re.sub(r"<[^>]+>", " ", melhor["content"]["rendered"]))
    return re.sub(r"\s+", " ", texto).strip()[:6000], melhor["link"]


_NOME = r"((?:[A-ZÁÂÃÉÊÍÓÔÕÚÇ][a-záâãéêíóôõúç]+)(?: (?:de |da |do |dos )?[A-ZÁÂÃÉÊÍÓÔÕÚÇ][a-záâãéêíóôõúç]+){0,3})"
RE_RELATOR = [
    re.compile(r"\b(?i:relator[a]?(?: d[aoe]s? \w+)?,? (?:o |a )?ministr[oa]) " + _NOME),
    re.compile(r"\b(?i:ministr[oa]) " + _NOME + r"[^.]{0,60}?\b(?:é|foi|será) (?:o |a )?relator"),
    re.compile(r"\b(?i:distribu[íi]d[ao] (?:ao|à) ministr[oa]) " + _NOME),
]


def extrair_sem_ia(texto: str) -> dict:
    """Extração simples por padrões, usada quando não há chave da IA."""
    proc = RE_PROCESSO.search(texto)
    rel = next((m for r in RE_RELATOR for m in [r.search(texto)] if m), None)
    placar = ""
    if re.search(r"\bpor unanimidade\b", texto, re.I):
        placar = "Unânime"
    else:
        m = re.search(r"\b(\d{1,2}) (?:votos )?a (\d{1,2})\b", texto)
        if m:
            placar = f"{m.group(1)} x {m.group(2)}"
    relator = rel.group(1) if rel else ""
    return {"processo": formatar_processo(proc), "relator": f"Min. {relator}" if relator else "", "placar": placar}


def preencher_fichas(noticias: list[dict], anterior: list[dict], usar_ia: bool) -> list[dict]:
    """Monta o painel: escolhe os casos, lê a notícia completa e preenche processo, relator e placar."""
    cache = {f.get("titulo_original") or f.get("tema"): f for f in anterior or []}
    escolhidas = candidatas_painel(noticias)[:8]
    if usar_ia:
        sel = selecionar_casos_ia(noticias)
        if sel is not None:
            escolhidas = sel

    fichas, pendentes = [], []
    for n in escolhidas:
        base = {"tribunal": n["tribunal"], "tema": n.get("tema") or n["titulo"], "titulo_original": n["titulo"],
                "processo": n.get("processo", ""), "relator": "", "placar": "", "status": n.get("status", "Em pauta"),
                "link": n["link"], "data": n["data"]}
        antigo = cache.get(n["titulo"])
        if antigo and (antigo.get("relator") or antigo.get("placar")):
            fichas.append({**base, **{k: antigo.get(k, "") for k in ("tema", "processo", "relator", "placar", "status", "link")}})
            continue
        if n["tribunal"] == "STF":
            achado = texto_stf(n["titulo"])
            if achado:
                base["texto"], base["link"] = achado
                if not usar_ia:
                    base.update({k: v for k, v in extrair_sem_ia(achado[0]).items() if v})
        fichas.append(base)
        pendentes.append(base)

    if usar_ia and pendentes:
        notas_stj = pesquisar_stj([f for f in pendentes if f["tribunal"] == "STJ" and not f.get("texto")])
        for f in pendentes:
            if f["tribunal"] == "STJ" and f["titulo_original"] in notas_stj:
                f["texto"] = notas_stj[f["titulo_original"]]
        extrair_com_ia([f for f in pendentes if f.get("texto")])

    for f in fichas:
        f.pop("texto", None)
    return fichas


# ---------------------------------------------------------------- IA (opcional)
def selecionar_casos_ia(noticias: list[dict]) -> list[dict] | None:
    candidatas = [n for n in noticias if n["tipo"] in ("pauta", "decisao")][:40]
    if not candidatas:
        return []
    dados = perguntar_claude(
        "Selecione até 8 casos que estão em pauta ou em julgamento (não incluídos os já encerrados há dias). "
        "Prefira casos de grande repercussão, do Plenário do STF e das Seções/Corte Especial do STJ. "
        "Ignore notícias de pauta genéricas ('confira a pauta'). Para cada caso, escreva o tema em até 15 "
        "palavras e indique o status provável pelo título.\n\n" + listar(candidatas),
        ESQUEMA_SELECAO,
    )
    if dados is None:
        return None
    saida = []
    for f in dados.get("casos", []):
        i = f.get("indice")
        if isinstance(i, int) and 0 <= i < len(candidatas):
            saida.append({**candidatas[i], "tema": f["tema"], "status": f["status"]})
    return saida


def pesquisar_stj(fichas: list[dict]) -> dict[str, str]:
    """O STJ bloqueia leitura automatizada do site; o Claude pesquisa em stj.jus.br com a busca na web."""
    if not fichas:
        return {}
    import anthropic

    client = anthropic.Anthropic()
    pedido = (
        "Para cada notícia do STJ abaixo, pesquise em stj.jus.br e anote, em texto corrido, o número do "
        "processo, o nome do(a) ministro(a) relator(a), o órgão julgador e o resultado ou placar da votação, "
        "se houver. Escreva apenas o que encontrar nas páginas do STJ. Responda com um bloco por notícia, "
        "começando pela linha '### [n]'.\n\n" + "\n".join(f"[{i}] {f['titulo_original']}" for i, f in enumerate(fichas))
    )
    mensagens = [{"role": "user", "content": pedido}]
    ferramentas = [{"type": "web_search_20260209", "name": "web_search",
                    "allowed_domains": ["stj.jus.br"], "max_uses": min(10, 2 * len(fichas))}]
    texto = ""
    try:
        for _ in range(4):  # retoma até 3 vezes se a busca pausar (pause_turn)
            r = client.beta.messages.create(
                model=MODELO, max_tokens=16000, betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                system=SISTEMA, output_config={"effort": "medium"}, tools=ferramentas, messages=mensagens,
            )
            texto += "".join(b.text for b in r.content if b.type == "text")
            if r.stop_reason != "pause_turn":
                break
            mensagens = [{"role": "user", "content": pedido}, {"role": "assistant", "content": r.content}]
    except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
        print(f"IA: pesquisa no STJ falhou ({e.__class__.__name__}); seguindo sem ela.", file=sys.stderr)
        return {}
    notas = {}
    for bloco in re.split(r"^###\s*", texto, flags=re.M):
        m = re.match(r"\[(\d+)\]", bloco)
        if m and int(m.group(1)) < len(fichas):
            notas[fichas[int(m.group(1))]["titulo_original"]] = bloco[m.end():].strip()[:3000]
    return notas


def extrair_com_ia(fichas: list[dict]) -> None:
    if not fichas:
        return
    blocos = "\n\n".join(f"[{i}] {f['tribunal']} · {f['titulo_original']}\n{f['texto']}" for i, f in enumerate(fichas))
    dados = perguntar_claude(
        "Para cada caso abaixo, extraia do texto o número do processo (ex.: ADI 7939, RE 1234567, Tema 1.485, "
        "REsp 2.000.000), o nome do(a) relator(a) no formato 'Min. Nome Sobrenome', o placar (ex.: '6 x 2', "
        "'Unânime', 'Maioria') e o status atual. Use somente o que o texto informa; se algo não estiver no "
        "texto, deixe o campo vazio.\n\n" + blocos,
        ESQUEMA_EXTRACAO,
    )
    if not dados:
        return
    for c in dados.get("casos", []):
        i = c.get("indice")
        if isinstance(i, int) and 0 <= i < len(fichas):
            for k in ("processo", "relator", "placar", "status"):
                if c.get(k):
                    fichas[i][k] = c[k]


SISTEMA = (
    "Você apoia a Liga Acadêmica de Tribunais Superiores da UFRN (LATS), que publica um informativo "
    "para estudantes de Direito sobre o STF e o STJ, a partir de notícias oficiais dos tribunais. "
    "Escreva em português do Brasil, em tom técnico e acessível. Nunca invente fatos: se um dado "
    "(relator, placar, número do processo, resultado) não estiver no material recebido, deixe-o vazio. "
    "Não emita opinião sobre o mérito das decisões."
)
STATUS = ["Em pauta", "Em julgamento", "Pedido de vista", "Suspenso", "Julgado"]
ESQUEMA_SELECAO = {
    "type": "object",
    "properties": {"casos": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "indice": {"type": "integer", "description": "Índice da notícia na lista recebida"},
            "tema": {"type": "string", "description": "Tema do caso em até 15 palavras"},
            "status": {"type": "string", "enum": STATUS},
        },
        "required": ["indice", "tema", "status"], "additionalProperties": False}}},
    "required": ["casos"], "additionalProperties": False,
}
ESQUEMA_EXTRACAO = {
    "type": "object",
    "properties": {"casos": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "indice": {"type": "integer"},
            "processo": {"type": "string"}, "relator": {"type": "string"}, "placar": {"type": "string"},
            "status": {"type": "string", "enum": STATUS},
        },
        "required": ["indice", "processo", "relator", "placar", "status"], "additionalProperties": False}}},
    "required": ["casos"], "additionalProperties": False,
}


ESQUEMA_ITEM = {
    "type": "object",
    "properties": {
        "indice": {"type": "integer"},
        "titulo": {"type": "string", "description": "Título reescrito, claro, até 14 palavras"},
        "resumo": {"type": "string", "description": "Uma ou duas frases explicando o que foi decidido e por que importa"},
    },
    "required": ["indice", "titulo", "resumo"],
    "additionalProperties": False,
}
ESQUEMA_INFORMATIVO = {
    "type": "object",
    "properties": {
        "titulo": {"type": "string", "description": "Manchete da edição, até 12 palavras"},
        "abertura": {"type": "string", "description": "Parágrafo de abertura com 2 ou 3 frases"},
        "stf": {"type": "array", "items": ESQUEMA_ITEM, "description": "Até 5 decisões mais relevantes do STF"},
        "stj": {"type": "array", "items": ESQUEMA_ITEM, "description": "Até 5 decisões mais relevantes do STJ"},
        "pauta": {"type": "array", "items": ESQUEMA_ITEM, "description": "Até 4 casos em pauta ou em julgamento"},
    },
    "required": ["titulo", "abertura", "stf", "stj", "pauta"],
    "additionalProperties": False,
}


def perguntar_claude(instrucao: str, esquema: dict) -> dict | None:
    import anthropic  # instalado só quando a IA está ligada

    client = anthropic.Anthropic()
    try:
        resposta = client.beta.messages.create(
            model=MODELO,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=SISTEMA,
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": esquema}},
            messages=[{"role": "user", "content": instrucao}],
        )
    except anthropic.RateLimitError:
        print("IA: limite de uso atingido; seguindo sem IA.", file=sys.stderr)
        return None
    except anthropic.APIStatusError as e:
        print(f"IA: erro da API ({e.status_code}); seguindo sem IA.", file=sys.stderr)
        return None
    except anthropic.APIConnectionError:
        print("IA: falha de conexão; seguindo sem IA.", file=sys.stderr)
        return None
    if resposta.stop_reason in ("refusal", "max_tokens"):
        print(f"IA: resposta interrompida ({resposta.stop_reason}); seguindo sem IA.", file=sys.stderr)
        return None
    texto = next((b.text for b in resposta.content if b.type == "text"), "")
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        print("IA: resposta em formato inesperado; seguindo sem IA.", file=sys.stderr)
        return None


def listar(noticias: list[dict]) -> str:
    return "\n".join(f"[{i}] {n['tribunal']} · {n['data'][:10]} · {n['titulo']}" for i, n in enumerate(noticias))


def nova_edicao(noticias: list[dict], numero: int) -> dict | None:
    hoje = dt.date.today()
    semana = [n for n in noticias if n["tipo"] != "institucional"
              and dt.datetime.fromisoformat(n["data"]).date() >= hoje - dt.timedelta(days=7)]
    if len(semana) < 3:
        print("Informativo: poucas notícias na semana; edição não gerada.", file=sys.stderr)
        return None
    dados = perguntar_claude(
        "Redija a edição semanal do Informativo LATS a partir das notícias abaixo (últimos 7 dias). "
        "Escolha as decisões mais relevantes para estudantes de Direito, explique cada uma em linguagem "
        "acessível e indique os casos que seguem em pauta. Use o índice [n] para apontar a notícia de origem.\n\n"
        + listar(semana),
        ESQUEMA_INFORMATIVO,
    )
    if dados is None:
        return None

    def resolver(itens):
        saida = []
        for it in itens or []:
            i = it.get("indice")
            if isinstance(i, int) and 0 <= i < len(semana):
                saida.append({"titulo": it["titulo"], "resumo": it["resumo"],
                              "link": semana[i]["link"], "tribunal": semana[i]["tribunal"]})
        return saida

    return {
        "numero": numero,
        "semana": (hoje - dt.timedelta(days=7)).isoformat(),
        "publicadoEm": hoje.isoformat(),
        "titulo": dados["titulo"],
        "abertura": dados["abertura"],
        "stf": resolver(dados["stf"]),
        "stj": resolver(dados["stj"]),
        "pauta": resolver(dados["pauta"]),
        "geradoComIA": True,
    }


# ---------------------------------------------------------------- arquivo
def ler_js(caminho: Path, prefixo: str, padrao):
    if not caminho.exists():
        return padrao
    texto = caminho.read_text(encoding="utf-8").strip()
    if texto.startswith(prefixo):
        texto = texto[len(prefixo):].rstrip(";")
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return padrao


def gravar_js(caminho: Path, prefixo: str, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(prefixo + json.dumps(dados, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--informativo", action="store_true", help="gera uma nova edição do Informativo LATS (requer IA)")
    ap.add_argument("--sem-ia", action="store_true", help="não usa o Claude mesmo que haja chave")
    args = ap.parse_args()

    anterior = ler_js(SAIDA, PREFIXO, {})
    noticias: list[dict] = []
    for tribunal, (consulta, origem) in FONTES.items():
        try:
            itens = coletar(tribunal, consulta, origem)
            print(f"{tribunal}: {len(itens)} notícias")
            noticias += itens
        except Exception as e:  # uma fonte fora do ar não derruba a atualização
            print(f"{tribunal}: falha na coleta ({e}); mantendo as notícias anteriores.", file=sys.stderr)
            noticias += [n for n in anterior.get("noticias", []) if n.get("tribunal") == tribunal]
    noticias.sort(key=lambda n: n["data"], reverse=True)

    usar_ia = not args.sem_ia and (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))

    if args.informativo:
        # modo semanal: grava só o arquivo do Informativo (vai para revisão num Pull Request)
        if not usar_ia:
            print("Informativo: defina ANTHROPIC_API_KEY para gerar a edição automática.", file=sys.stderr)
            return 1
        informativos = ler_js(SAIDA_INFO, PREFIXO_INFO, [])
        numero = max((e.get("numero", 0) for e in informativos), default=0) + 1
        edicao = nova_edicao(noticias, numero)
        if not edicao:
            return 1
        gravar_js(SAIDA_INFO, PREFIXO_INFO, ([edicao] + informativos)[:MAX_EDICOES])
        print(f"Informativo nº {numero} gerado: {edicao['titulo']}")
        return 0

    painel = preencher_fichas(noticias, anterior.get("emJulgamento", []), bool(usar_ia))
    gravar_js(SAIDA, PREFIXO, {
        "atualizadoEm": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
        "fonte": "Notícias oficiais de stf.jus.br e stj.jus.br, coletadas via Google Notícias",
        "painelComIA": bool(usar_ia),
        "emJulgamento": painel,
        "noticias": noticias,
    })
    print(f"Gravado em {SAIDA.relative_to(RAIZ)} · {len(noticias)} notícias · {len(painel)} fichas")
    return 0


if __name__ == "__main__":
    sys.exit(main())

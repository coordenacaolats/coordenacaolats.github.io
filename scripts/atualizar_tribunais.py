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
    r"\b(ADI|ADPF|ADC|ADO|RE|ARE|HC|RHC|REsp|AREsp|MS|MI|Rcl|EREsp|IAC|Tema)\s*(n[ºo°.]*\s*)?(\d[\d.]*)", re.I)


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


def painel_heuristico(noticias: list[dict]) -> list[dict]:
    """Sem IA: o painel lista as notícias de pauta/julgamento mais recentes."""
    fichas = []
    for n in noticias:
        if n["tipo"] != "pauta" or re.search(r"confira a pauta|destaques da pauta", n["titulo"], re.I):
            continue
        fichas.append({
            "tribunal": n["tribunal"], "tema": n["titulo"], "processo": n["processo"],
            "relator": "", "placar": "", "status": "Em pauta", "link": n["link"], "data": n["data"],
        })
    return fichas[:8]


# ---------------------------------------------------------------- IA (opcional)
SISTEMA = (
    "Você apoia a Liga Acadêmica de Tribunais Superiores da UFRN (LATS), que publica um informativo "
    "para estudantes de Direito sobre o STF e o STJ. Você recebe apenas títulos e datas de notícias "
    "oficiais dos tribunais. Escreva em português do Brasil, em tom técnico e acessível. "
    "Nunca invente fatos: se um dado (relator, placar, número do processo, resultado) não estiver no "
    "título, deixe o campo vazio. Não emita opinião sobre o mérito das decisões."
)

ESQUEMA_PAINEL = {
    "type": "object",
    "properties": {
        "fichas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "indice": {"type": "integer", "description": "Índice da notícia na lista recebida"},
                    "tema": {"type": "string", "description": "Tema do caso em até 15 palavras"},
                    "processo": {"type": "string"},
                    "relator": {"type": "string"},
                    "placar": {"type": "string"},
                    "status": {"type": "string", "enum": ["Em pauta", "Em julgamento", "Pedido de vista", "Suspenso", "Julgado"]},
                },
                "required": ["indice", "tema", "processo", "relator", "placar", "status"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["fichas"],
    "additionalProperties": False,
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


def painel_ia(noticias: list[dict]) -> list[dict] | None:
    candidatas = [n for n in noticias if n["tipo"] in ("pauta", "decisao")][:40]
    if not candidatas:
        return []
    dados = perguntar_claude(
        "Selecione até 8 casos que estão em pauta ou em julgamento (não incluídos os já encerrados há dias) "
        "e monte uma ficha para cada um. Prefira casos de grande repercussão, do Plenário do STF e das "
        "Seções/Corte Especial do STJ. Ignore notícias de pauta genéricas ('confira a pauta').\n\n"
        + listar(candidatas),
        ESQUEMA_PAINEL,
    )
    if dados is None:
        return None
    fichas = []
    for f in dados.get("fichas", []):
        i = f.get("indice")
        if not isinstance(i, int) or not 0 <= i < len(candidatas):
            continue
        n = candidatas[i]
        fichas.append({**{k: f.get(k, "") for k in ("tema", "processo", "relator", "placar", "status")},
                       "tribunal": n["tribunal"], "link": n["link"], "data": n["data"]})
    return fichas


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

    painel = painel_ia(noticias) if usar_ia else None
    if painel is None:
        painel = painel_heuristico(noticias)
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

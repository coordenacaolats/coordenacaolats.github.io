#!/usr/bin/env python3
"""
Fecha a edição do Informativo LATS depois que a revisão é aprovada:

  1. Se informativo/comentario-da-semana.md estiver preenchido, junta o comentário
     do membro à edição mais recente (só se ela ainda não foi enviada) e devolve
     o arquivo ao modelo em branco.
  2. Se a edição mais recente estiver marcada como "pendente" e houver as
     configurações da Brevo, cria a campanha e envia o e-mail aos inscritos.

Configuração (GitHub > Settings > Secrets and variables > Actions):
  segredo  BREVO_API_KEY       chave da API da Brevo
  variável BREVO_LIST_ID       número da lista de inscritos
  variável BREVO_SENDER_EMAIL  remetente verificado na Brevo
  variável BREVO_SENDER_NAME   (opcional) padrão: "Informativo LATS"

Uso:
  python scripts/informativo_email.py            # junta comentário e envia, se pendente
  python scripts/informativo_email.py --previa   # só grava a prévia do e-mail em HTML
  python scripts/informativo_email.py --verificar       # só confere a chave da Brevo
  python scripts/informativo_email.py --teste a@b.com   # envia só um teste para o endereço

Sem dependências externas.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INFO = RAIZ / "site" / "data" / "informativos.js"
PREFIXO = "window.LATS_INFORMATIVOS = "
COMENTARIO = RAIZ / "informativo" / "comentario-da-semana.md"
SITE = "https://latsufrn.com.br/"
API = "https://api.brevo.com/v3"

CAMPOS = {
    "autor": "Autor",
    "funcao": "Função na LATS",
    "decisao": "Decisão comentada",
    "link": "Link da decisão",
    "titulo": "Título do comentário",
}
MODELO = """<!--
  COMENTÁRIO DA SEMANA — Informativo LATS

  Cole aqui o comentário de um membro da Liga sobre uma decisão do STF (ou do STJ).
  Preencha cada campo depois dos dois-pontos e escreva o texto abaixo da linha "Texto:".
  Parágrafos: separe com uma linha em branco.

  Ao aprovar (Merge) a revisão do Informativo, o comentário entra na edição,
  vai para o site e segue no e-mail aos inscritos. Depois o arquivo volta em branco.
  Se deixar em branco, a edição sai sem comentário.
-->
""" + "".join(f"{r}: \n" for r in CAMPOS.values()) + "\nTexto:\n\n"


# ---------------------------------------------------------------- arquivos
def ler_info() -> list[dict]:
    t = INFO.read_text(encoding="utf-8").strip()
    return json.loads(t[len(PREFIXO):].rstrip(";")) if t.startswith(PREFIXO) else []


def gravar_info(eds: list[dict]) -> None:
    INFO.write_text(PREFIXO + json.dumps(eds, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")


def ler_comentario() -> dict | None:
    if not COMENTARIO.exists():
        return None
    t = re.sub(r"<!--.*?-->", "", COMENTARIO.read_text(encoding="utf-8"), flags=re.S)
    partes = re.split(r"^\s*Texto\s*:\s*$", t, maxsplit=1, flags=re.M)
    cab, corpo = partes[0], (partes[1] if len(partes) > 1 else "")
    c = {}
    for chave, rotulo in CAMPOS.items():
        m = re.search(rf"^\s*{re.escape(rotulo)}\s*:[ \t]*(.*)$", cab, flags=re.M)
        c[chave] = m.group(1).strip() if m else ""
    paragrafos = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", corpo.strip())]
    c["texto"] = [p for p in paragrafos if p]
    if not (c["autor"] and c["texto"]):
        return None
    if not c["titulo"]:
        c["titulo"] = c["decisao"] or "Comentário da semana"
    return {k: v for k, v in c.items() if v}


# ---------------------------------------------------------------- e-mail
def e(s) -> str:
    return html.escape(str(s or ""), quote=True)


def dia_longo(iso: str) -> str:
    meses = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
    d = dt.date.fromisoformat(iso[:10])
    return f"{d.day} de {meses[d.month - 1]} de {d.year}"


def data_da_edicao(ed: dict) -> tuple[str, str]:
    """Data do envio, no alto do e-mail: ('24/11/2026', 'terça-feira')."""
    dias = "segunda-feira terça-feira quarta-feira quinta-feira sexta-feira sábado domingo".split()
    d = dt.date.today() if ed.get("email") == "pendente" else dt.date.fromisoformat(ed.get("publicadoEm", ed["semana"])[:10])
    return d.strftime("%d/%m/%Y"), dias[d.weekday()]


def montar_html(ed: dict) -> str:
    NAVY, ICE, SAND, OURO, INK, CINZA = "#072A3E", "#D6E6F2", "#D6CCBE", "#8F7A58", "#1b2b36", "#5b6b77"
    serif = "Georgia,'Times New Roman',serif"
    sans = "Helvetica,Arial,sans-serif"
    P = "padding:0 40px;"
    url = SITE + "informativo.html#informativo"

    def rotulo(texto):
        return (f'<p style="margin:0;font-family:{sans};font-size:13px;font-weight:bold;letter-spacing:2px;line-height:1.5;'
                f'text-transform:uppercase;color:{OURO};text-align:center;">{e(texto)}</p>')

    def link(i, estilo):
        if not i.get("link"):
            return f'<span style="{estilo}">{e(i["titulo"])}</span>'
        return f'<a href="{e(i["link"])}" style="{estilo}text-decoration:none;">{e(i["titulo"])}</a>'

    divisor = (
        '<tr><td class="lado" style="padding:34px 40px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
        f'<td style="vertical-align:middle;"><div style="border-top:1px solid {SAND};font-size:0;line-height:0;">&nbsp;</div></td>'
        f'<td width="46" align="center" style="width:46px;"><img src="{SITE}assets/img/email/divisor.png" width="20" alt="" style="display:block;border:0;width:20px;height:auto;margin:0 auto;"></td>'
        f'<td style="vertical-align:middle;"><div style="border-top:1px solid {SAND};font-size:0;line-height:0;">&nbsp;</div></td>'
        '</tr></table></td></tr>')

    com = ed.get("comentario")

    # ---- quadro "Nesta edição"
    linhas = []
    if com:
        linhas.append(("Comentário", com["titulo"]))
    linhas += [("STF", i["titulo"]) for i in (ed.get("stf") or [])[:3]]
    linhas += [("STJ", i["titulo"]) for i in (ed.get("stj") or [])[:3]]
    quadro = "".join(
        f'<tr><td style="padding:{"0" if n == 0 else "14px"} 0 0;font-family:{sans};font-size:15px;line-height:1.5;color:{INK};text-align:center;">'
        f'<span style="font-size:11px;font-weight:bold;letter-spacing:1px;text-transform:uppercase;color:{OURO};">{e(t)}</span><br>{e(x)}</td></tr>'
        for n, (t, x) in enumerate(linhas))
    if quadro:
        quadro = (
            f'<tr><td class="lado" style="padding:34px 40px 18px;">{rotulo("Nesta edição")}</td></tr>'
            f'<tr><td class="lado" style="{P}"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:#F3F8FC;border:1px solid {NAVY};border-radius:10px;border-collapse:separate;"><tr><td style="padding:26px 24px;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{quadro}</table></td></tr></table></td></tr>')

    # ---- comentário do membro da Liga
    bloco_com = ""
    if com:
        paras = "".join(f'<p style="margin:0 0 16px;font-family:{serif};font-size:17px;line-height:1.65;color:{INK};">{e(p)}</p>' for p in com["texto"])
        dec = ""
        if com.get("decisao"):
            alvo = f'<a href="{e(com["link"])}" style="color:{NAVY};font-weight:bold;">{e(com["decisao"])}</a>' if com.get("link") else f'<b>{e(com["decisao"])}</b>'
            dec = f'<p style="margin:14px 0 0;font-family:{sans};font-size:14px;line-height:1.5;color:{CINZA};text-align:center;">Sobre: {alvo}</p>'
        funcao = f'<br><span style="color:{CINZA};">{e(com["funcao"])}</span>' if com.get("funcao") else ""
        bloco_com = divisor + (
            f'<tr><td class="lado" style="{P}">{rotulo("Comentário LATS")}'
            f'<h2 class="tit" style="margin:14px 0 0;font-family:{serif};font-weight:bold;font-size:27px;line-height:1.25;color:{NAVY};text-align:center;">{e(com["titulo"])}</h2>'
            f'{dec}</td></tr>'
            f'<tr><td class="lado" style="padding:24px 40px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:{ICE};border-radius:10px;border-collapse:separate;"><tr><td style="padding:28px 28px 26px;">{paras}'
            f'<p style="margin:4px 0 0;padding-top:16px;border-top:1px solid #b4c9d9;font-family:{sans};font-size:14px;line-height:1.5;color:{NAVY};">'
            f'por <b>{e(com["autor"])}</b>{funcao}</p></td></tr></table></td></tr>')

    # ---- tribunais: a primeira decisão em destaque, as demais em sequência
    def tribunal(nome, itens):
        if not itens:
            return ""
        d, resto = itens[0], itens[1:]
        est = f"font-family:{serif};font-weight:bold;font-size:27px;line-height:1.25;color:{NAVY};"
        s = divisor + (
            f'<tr><td class="lado" style="{P}">{rotulo(nome)}'
            f'<h2 class="tit" style="margin:14px 0 18px;{est}text-align:center;">{link(d, est)}</h2>'
            + (f'<p style="margin:0;font-family:{sans};font-size:16px;line-height:1.65;color:{INK};">{e(d["resumo"])}</p>' if d.get("resumo") else "")
            + '</td></tr>')
        est2 = f"font-family:{serif};font-weight:bold;font-size:18px;line-height:1.35;color:{NAVY};"
        for i in resto:
            s += (f'<tr><td class="lado" style="padding:22px 40px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>'
                  f'<td style="border-left:3px solid {SAND};padding:2px 0 2px 18px;">{link(i, est2)}'
                  + (f'<p style="margin:7px 0 0;font-family:{sans};font-size:15px;line-height:1.6;color:{INK};">{e(i["resumo"])}</p>' if i.get("resumo") else "")
                  + '</td></tr></table></td></tr>')
        return s

    # ---- na pauta
    pauta = ""
    if ed.get("pauta"):
        est3 = f"font-family:{sans};font-weight:bold;font-size:15px;line-height:1.45;color:{NAVY};"
        itens = "".join(
            f'<tr><td style="padding:{"0" if n == 0 else "18px"} 0 0;">{link(i, est3)}'
            + (f'<p style="margin:5px 0 0;font-family:{sans};font-size:14px;line-height:1.6;color:{INK};">{e(i["resumo"])}</p>' if i.get("resumo") else "")
            + '</td></tr>' for n, i in enumerate(ed["pauta"]))
        pauta = divisor + (
            f'<tr><td class="lado" style="{P}">{rotulo("Na pauta")}'
            f'<h2 class="tit" style="margin:14px 0 20px;font-family:{serif};font-weight:bold;font-size:27px;line-height:1.25;color:{NAVY};text-align:center;">O que vem por aí nos Tribunais</h2></td></tr>'
            f'<tr><td class="lado" style="{P}"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:#F7F4EF;border:1px solid {SAND};border-radius:10px;border-collapse:separate;"><tr><td style="padding:26px 24px;">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{itens}</table></td></tr></table></td></tr>')

    dia, semana = data_da_edicao(ed)
    nota_ia = (f'<p style="margin:24px 0 0;font-family:{sans};font-size:12px;line-height:1.6;color:{CINZA};text-align:center;">Resumos elaborados com auxílio de inteligência artificial '
               'a partir das notícias oficiais do STF e do STJ e revisados pela equipe da LATS.</p>') if ed.get("geradoComIA") else ""

    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><meta name="supported-color-schemes" content="light">
<title>{e(ed['titulo'])}</title>
<style>@media (max-width:520px){{.lado{{padding-left:22px!important;padding-right:22px!important}}.tit{{font-size:23px!important}}.h1{{font-size:27px!important}}}}</style></head>
<body style="margin:0;padding:0;background:#ffffff;">
<div style="display:none;max-height:0;overflow:hidden;">{e((ed.get('abertura') or '')[:150])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#ffffff;"><tr><td align="center" style="padding:0;">
<table role="presentation" width="620" cellpadding="0" cellspacing="0" style="max-width:620px;width:100%;background:#ffffff;">
<tr><td align="center" style="background:{NAVY};padding:30px 24px 26px;">
  <a href="{SITE}" style="text-decoration:none;"><img src="{SITE}assets/img/email/logo-topo.png" width="150" alt="LATS" style="display:block;border:0;width:150px;height:auto;margin:0 auto;"></a>
  <p style="margin:16px 0 0;font-family:{sans};font-size:12px;letter-spacing:2px;text-transform:uppercase;color:{SAND};">Informativo · Nº {int(ed['numero']):02d}</p>
</td></tr>
<tr><td class="lado" style="padding:34px 40px 0;text-align:center;">
  <p style="margin:0;font-family:{sans};font-size:17px;font-weight:bold;line-height:1.5;color:{NAVY};">{dia}<br>{semana}</p>
  <h1 class="h1" style="margin:22px 0 18px;font-family:{serif};font-weight:bold;font-size:33px;line-height:1.2;color:{NAVY};">{e(ed['titulo'])}</h1>
  <p style="margin:0;font-family:{sans};font-size:16px;line-height:1.65;color:{INK};">{e(ed.get('abertura'))}</p>
</td></tr>
{quadro}
{bloco_com}
{tribunal("Supremo Tribunal Federal", ed.get("stf"))}
{tribunal("Superior Tribunal de Justiça", ed.get("stj"))}
{pauta}
{divisor}
<tr><td class="lado" align="center" style="padding:0 40px 40px;">
  <p style="margin:0 0 20px;font-family:{serif};font-size:20px;line-height:1.4;color:{NAVY};">Até a próxima semana!</p>
  <a href="{url}" style="display:inline-block;background:{NAVY};color:#ffffff;font-family:{sans};font-size:14px;font-weight:bold;text-decoration:none;padding:14px 28px;border-radius:8px;">Ler no site da LATS</a>
  {nota_ia}
</td></tr>
<tr><td align="center" style="background:{NAVY};padding:26px 32px;font-family:{sans};font-size:12px;line-height:1.8;color:#b5c6d3;text-align:center;">
  Liga Acadêmica de Tribunais Superiores · UFRN<br>
  <a href="{SITE}" style="color:{ICE};">latsufrn.com.br</a> &nbsp;·&nbsp; <a href="https://www.instagram.com/latsufrn/" style="color:{ICE};">@latsufrn</a><br><br>
  Você recebe este e-mail porque se inscreveu no Informativo LATS.<br><a href="{{{{ unsubscribe }}}}" style="color:{ICE};">Cancelar inscrição</a>
</td></tr>
</table></td></tr></table></body></html>"""


def brevo(metodo: str, caminho: str, corpo: dict | None = None):
    req = urllib.request.Request(
        API + caminho, method=metodo,
        data=json.dumps(corpo).encode() if corpo is not None else None,
        headers={"api-key": os.environ["BREVO_API_KEY"], "content-type": "application/json", "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode() or "{}"
            return json.loads(t)
    except urllib.error.HTTPError as err:
        raise SystemExit(f"Brevo {metodo} {caminho}: HTTP {err.code} — {err.read().decode(errors='replace')}")


def criar_campanha(ed: dict) -> int:
    assunto = f"Informativo LATS nº {ed['numero']} — {ed['titulo']}"
    r = brevo("POST", "/emailCampaigns", {
        "name": f"Informativo LATS nº {ed['numero']}",
        "subject": assunto[:200],
        "previewText": (ed.get("abertura") or "")[:150],
        "sender": {"name": os.environ.get("BREVO_SENDER_NAME") or "Informativo LATS",
                   "email": os.environ["BREVO_SENDER_EMAIL"]},
        "htmlContent": montar_html(ed),
        "recipients": {"listIds": [int(os.environ["BREVO_LIST_ID"])]},
    })
    return int(r["id"])


def configurado() -> bool:
    falta = [v for v in ("BREVO_API_KEY", "BREVO_LIST_ID", "BREVO_SENDER_EMAIL") if not os.environ.get(v)]
    if falta:
        print("E-mail não enviado: faltam " + ", ".join(falta) + ".", file=sys.stderr)
    return not falta


# ---------------------------------------------------------------- principal
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--previa", action="store_true", help="grava a prévia do e-mail em informativo/previa-email.html")
    ap.add_argument("--teste", metavar="EMAIL", help="envia só um e-mail de teste da edição mais recente")
    ap.add_argument("--verificar", action="store_true", help="só confere se a Brevo aceita a chave (não envia nada)")
    args = ap.parse_args()

    if args.verificar:
        if not os.environ.get("BREVO_API_KEY"):
            raise SystemExit("Falta BREVO_API_KEY.")
        r = brevo("GET", "/emailCampaigns?limit=1")
        print(f"A Brevo aceitou a chave. Campanhas na conta: {r.get('count', 0)}.")
        return 0

    eds = ler_info()
    if not eds:
        print("Nenhuma edição do Informativo.")
        return 0
    ed = eds[0]
    mudou = False

    # 1) comentário do membro
    com = ler_comentario()
    if com and ed.get("email") == "pendente" and not ed.get("comentario"):
        ed["comentario"] = com
        COMENTARIO.write_text(MODELO, encoding="utf-8")
        mudou = True
        print(f"Comentário de {com['autor']} incluído no Informativo nº {ed['numero']}.")
    elif com:
        print("Comentário preenchido, mas a edição mais recente já foi enviada; ele aguarda a próxima.")

    if args.previa or args.teste:
        destino = RAIZ / "informativo" / "previa-email.html"
        destino.write_text(montar_html(ed), encoding="utf-8")
        print(f"Prévia gravada em {destino.relative_to(RAIZ)}")
        if args.teste and configurado():
            cid = criar_campanha({**ed, "titulo": "[TESTE] " + ed["titulo"]})
            brevo("POST", f"/emailCampaigns/{cid}/sendTest", {"emailTo": [args.teste]})
            print(f"Teste enviado (campanha {cid}).")
        if mudou:
            gravar_info(eds)
        return 0

    # 2) envio
    if ed.get("email") == "pendente":
        publicado = dt.date.fromisoformat(ed.get("publicadoEm", "1970-01-01")[:10])
        if dt.date.today() - publicado > dt.timedelta(days=10):
            ed["email"] = "não enviado (edição antiga)"
            mudou = True
        elif configurado():
            cid = criar_campanha(ed)
            brevo("POST", f"/emailCampaigns/{cid}/sendNow")
            ed["email"] = dt.date.today().isoformat()
            ed["emailCampanha"] = cid
            mudou = True
            print(f"Informativo nº {ed['numero']} enviado por e-mail (campanha {cid}).")

    if mudou:
        gravar_info(eds)
    return 0


if __name__ == "__main__":
    sys.exit(main())

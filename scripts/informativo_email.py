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


def montar_html(ed: dict) -> str:
    NAVY, ICE, SAND, INK = "#072A3E", "#D6E6F2", "#C9B79C", "#1b2b36"
    serif = "Georgia,'Times New Roman',serif"
    sans = "Helvetica,Arial,sans-serif"

    def bloco(titulo, itens):
        if not itens:
            return ""
        lis = "".join(
            f'<tr><td style="padding:0 0 18px 0;">'
            f'<a href="{e(i.get("link"))}" style="font-family:{serif};font-size:18px;line-height:1.35;color:{NAVY};text-decoration:none;font-weight:bold;">{e(i["titulo"])}</a>'
            + (f'<p style="margin:6px 0 0;font-family:{sans};font-size:15px;line-height:1.6;color:{INK};">{e(i.get("resumo"))}</p>' if i.get("resumo") else "")
            + "</td></tr>" for i in itens)
        return (f'<tr><td style="padding:26px 36px 4px;"><p style="margin:0 0 14px;font-family:{sans};font-size:11px;letter-spacing:3px;'
                f'text-transform:uppercase;color:#7a8a96;border-bottom:1px solid #e3e9ee;padding-bottom:8px;">{e(titulo)}</p>'
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0">{lis}</table></td></tr>')

    com = ed.get("comentario")
    bloco_com = ""
    if com:
        paras = "".join(f'<p style="margin:0 0 12px;font-family:{serif};font-size:17px;line-height:1.65;color:{INK};">{e(p)}</p>' for p in com["texto"])
        dec = ""
        if com.get("decisao"):
            dec = (f'<a href="{e(com["link"])}" style="color:{NAVY};">{e(com["decisao"])}</a>' if com.get("link") else e(com["decisao"]))
            dec = f'<p style="margin:0 0 14px;font-family:{sans};font-size:13px;color:#5b6b77;">Sobre: {dec}</p>'
        bloco_com = (
            f'<tr><td style="padding:26px 36px 8px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
            f'style="background:#f1f6fa;border-left:4px solid {NAVY};"><tr><td style="padding:24px 26px;">'
            f'<p style="margin:0 0 8px;font-family:{sans};font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7a8a96;">Comentário LATS</p>'
            f'<p style="margin:0 0 10px;font-family:{serif};font-size:22px;line-height:1.3;color:{NAVY};">{e(com["titulo"])}</p>'
            f'{dec}{paras}'
            f'<p style="margin:14px 0 0;font-family:{sans};font-size:14px;color:{NAVY};"><b>{e(com["autor"])}</b>'
            + (f'<br><span style="color:#5b6b77;">{e(com.get("funcao"))}</span>' if com.get("funcao") else "")
            + '</p></td></tr></table></td></tr>')

    url = SITE + "informativo.html#informativo"
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(ed['titulo'])}</title></head>
<body style="margin:0;padding:0;background:#eef2f5;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef2f5;"><tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%;background:#ffffff;">
<tr><td style="background:{NAVY};padding:30px 36px;">
  <img src="{SITE}assets/img/logo-h.png" width="150" alt="LATS" style="display:block;border:0;width:150px;height:auto;">
  <p style="margin:18px 0 0;font-family:{sans};font-size:11px;letter-spacing:3px;text-transform:uppercase;color:{SAND};">Informativo LATS · Nº {int(ed['numero']):02d} · Semana de {dia_longo(ed['semana'])}</p>
</td></tr>
<tr><td style="padding:32px 36px 6px;">
  <h1 style="margin:0 0 14px;font-family:{serif};font-weight:normal;font-size:28px;line-height:1.2;color:{NAVY};">{e(ed['titulo'])}</h1>
  <p style="margin:0;font-family:{sans};font-size:15px;line-height:1.65;color:{INK};">{e(ed.get('abertura'))}</p>
</td></tr>
{bloco_com}
{bloco("Supremo Tribunal Federal", ed.get("stf"))}
{bloco("Superior Tribunal de Justiça", ed.get("stj"))}
{bloco("Na pauta", ed.get("pauta"))}
<tr><td style="padding:10px 36px 34px;">
  <a href="{url}" style="display:inline-block;background:{NAVY};color:{ICE};font-family:{sans};font-size:12px;letter-spacing:2px;text-transform:uppercase;text-decoration:none;padding:14px 22px;">Ler no site</a>
  {'<p style="margin:22px 0 0;font-family:' + sans + ';font-size:12px;line-height:1.5;color:#7a8a96;">Resumos elaborados com auxílio de inteligência artificial a partir das notícias oficiais do STF e do STJ e revisados pela equipe da LATS.</p>' if ed.get("geradoComIA") else ""}
</td></tr>
<tr><td style="background:{NAVY};padding:22px 36px;font-family:{sans};font-size:12px;line-height:1.6;color:#9fb3c2;">
  Liga Acadêmica de Tribunais Superiores · UFRN<br>
  <a href="{SITE}" style="color:{ICE};">latsufrn.com.br</a> · <a href="https://www.instagram.com/latsufrn/" style="color:{ICE};">@latsufrn</a><br>
  Você recebe este e-mail porque se inscreveu no Informativo LATS. <a href="{{{{ unsubscribe }}}}" style="color:{ICE};">Cancelar inscrição</a>
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
        "tag": "informativo",
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
    args = ap.parse_args()

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

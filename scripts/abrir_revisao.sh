#!/bin/bash
# Monta a edição do Informativo LATS e abre (ou atualiza) a revisão no GitHub, sem usar a API do Claude.
# Uso: scripts/abrir_revisao.sh noticias.json edicao.json
# Trabalha numa cópia temporária: não mexe na pasta do site nem publica nada.
# Não faz Merge. O Merge, feito por um membro da Liga, publica a edição e envia o e-mail.
set -euo pipefail
NOTICIAS=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
EDICAO=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
GH=$(command -v gh || echo "$HOME/.local/bin/gh")
RAMO=informativo/semana
cd "$RAIZ"
git fetch -q origin

PR=$("$GH" pr list --head "$RAMO" --state open --json number -q '.[0].number // empty')
TMP=$(mktemp -d)
trap 'git -C "$RAIZ" worktree remove --force "$TMP/site" 2>/dev/null || true; rm -rf "$TMP"' EXIT

if [ -n "$PR" ]; then
  git fetch -q origin "+refs/heads/$RAMO:refs/remotes/origin/$RAMO"
  git worktree add -q --detach "$TMP/site" "origin/$RAMO"
  if (cd "$TMP/site" && python3 -B -c "import sys; sys.path.insert(0,'scripts'); import informativo_email as i; sys.exit(0 if i.ler_comentario() else 1)"); then
    echo "PARADO: a revisão aberta (PR $PR) já tem comentário de um membro. Nada foi alterado." >&2
    exit 3
  fi
  AUTORES=$(git log --format='%an' "origin/main..origin/$RAMO" | wc -l | tr -d ' ')
  if [ "$AUTORES" -gt 1 ]; then
    echo "PARADO: a revisão aberta (PR $PR) já recebeu edições. Nada foi alterado." >&2
    exit 3
  fi
  git worktree remove --force "$TMP/site"
fi

git worktree add -q --detach "$TMP/site" origin/main
cd "$TMP/site"
python3 -B scripts/atualizar_tribunais.py --aplicar-edicao "$NOTICIAS" "$EDICAO"
NUM=$(python3 -c "import json;t=open('site/data/informativos.js').read();print(json.loads(t[t.index('['):].rstrip().rstrip(';'))[0]['numero'])")
git add site/data/informativos.js informativo/comentario-da-semana.md
git commit -qm "Informativo LATS nº $NUM: edição para revisão

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q --force origin "HEAD:refs/heads/$RAMO"

cat > "$TMP/corpo.md" <<'C'
Edição redigida pelo Claude a partir das notícias oficiais do STF e do STJ.

**1. Comentário LATS (opcional)**
Em *Files changed*, abra `informativo/comentario-da-semana.md` › menu ⋯ › *Edit file*. Cole o comentário do membro (autor, função, decisão, link, título e texto) e clique em *Commit changes*. Se ficar em branco, a edição sai sem comentário.

**2. Antes de aprovar, confira:**
- [ ] Os resumos correspondem ao que foi decidido (abra os links, sobretudo os do STJ).
- [ ] Não há opinião sobre o mérito nem dado que não esteja na notícia.
- [ ] O título e a abertura estão adequados.

Para corrigir um resumo, edite `site/data/informativos.js` nesta branch.

**3. Merge** — a edição vai para o site e, em seguida, **o e-mail é enviado aos inscritos**. Aprove em até 10 dias.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
C
TITULO="Informativo LATS nº $NUM — revisão"
if [ -n "$PR" ]; then
  "$GH" pr edit "$PR" --title "$TITULO" --body-file "$TMP/corpo.md"
else
  "$GH" pr create --base main --head "$RAMO" --title "$TITULO" --body-file "$TMP/corpo.md"
fi

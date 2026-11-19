#!/usr/bin/env bash
# Uso: demo/inject.sh {secret|sast|dep|docker}
# Cria uma branch, injeta UMA falha grave, commita e faz push -> pipeline deve falhar.
# Para corrigir ao vivo: git revert --no-edit HEAD && git push
set -euo pipefail
tipo="${1:?uso: $0 secret|sast|dep|docker}"
git checkout -b "demo/falha-$tipo"
case "$tipo" in
  secret)  # token montado em runtime p/ o proprio script nao ser flagado
    printf 'GITHUB_TOKEN = "%s%s"\n' "ghp_" "aB3dE5gH7jK9mN1pQ3rS5tU7vW9xY1zA3bC5" > app/config_demo.py ;;
  sast)
    cat > app/vuln_demo.py <<'PY'
import sqlite3, subprocess

def find_user(name):
    conn = sqlite3.connect("db.sqlite")
    return conn.execute(f"SELECT * FROM users WHERE name = '{name}'").fetchall()  # SQL Injection

def ping(host):
    return subprocess.run("ping -c1 " + host, shell=True)  # Command Injection
PY
    ;;
  dep)
    echo "pyyaml==5.3.1" >> requirements.txt ;;   # CVE critica conhecida
  docker)
    sed -i 's/^USER 10001/USER root/' Dockerfile ;;
  *) echo "tipo invalido"; exit 1 ;;
esac
git add -A
git commit -m "demo: falha intencional ($tipo)"
git push -u origin HEAD

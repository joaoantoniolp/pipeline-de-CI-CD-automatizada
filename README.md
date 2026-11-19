# Esteira DevSecOps — FastAPI + GitHub Actions

API FastAPI simples + Docker + IaC (Compose e Kubernetes) protegidos por uma esteira com Security Gates.

| Etapa | Ferramenta | Gate |
|---|---|---|
| Secret scanning | Gitleaks | qualquer segredo |
| SAST | Semgrep (python, owasp-top-ten, security-audit) | `--error` |
| SCA + SBOM | Trivy (CVEs) + Syft (CycloneDX, artefato `sbom.cdx.json`) | HIGH/CRITICAL |
| Dockerfile / IaC | Hadolint, Checkov, Trivy config | warning / falhas / HIGH+ |
| Imagem | Trivy image | HIGH/CRITICAL |
| DAST | OWASP ZAP API scan (OpenAPI) | falha em alertas |

O job `build-dast` só roda se todos os anteriores passarem (`needs`).

## Setup
1. Crie um repositório no GitHub, suba este código na `main`, confirme a esteira verde.
2. Rodar local: `API_KEY=minha-chave docker compose up --build` → http://127.0.0.1:8000/docs

## Roteiro da demo
1. Mostrar estrutura + `.github/workflows/devsecops.yml`.
2. Falha: `demo/inject.sh secret` (ou `sast`, `dep`, `docker`) → abrir Actions → job vermelho.
3. Correção: `git revert --no-edit HEAD && git push` → tudo verde.
4. Mostrar artefato `sbom.cdx.json` e logs de Semgrep/Trivy/ZAP.

## Notas
- Troque `SEU_USUARIO` em `k8s/deployment.yaml`.
- Na primeira execução, o ZAP pode gerar alertas a ajustar em `.zap/rules.tsv`.

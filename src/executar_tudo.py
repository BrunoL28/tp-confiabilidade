"""Roda as etapas 2 a 4 na ordem e grava o que cada uma imprime em saida/execucao_pipeline.md."""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).parent
SAIDA = SRC.parent / "saida" / "execucao_pipeline.md"
ETAPAS = ["02_tratar_ntsb.py", "03_analise_confiabilidade.py", "04_bayes_weibull.py"]


def para_markdown(texto):
    """Cada bloco '== título' vira uma subseção com a tabela em bloco de código; avisos viram citação."""
    partes, titulo, linhas = [], None, []

    def fechar():
        corpo = "\n".join(linhas).strip("\n")
        if titulo:
            partes.append(f"### {titulo}\n\n```text\n{corpo}\n```\n")
        elif corpo:
            partes.append("\n".join(f"> {l}" for l in corpo.splitlines() if l.strip()) + "\n")

    for linha in texto.splitlines():
        if linha.startswith("== "):
            fechar()
            titulo, linhas = linha[3:].strip(), []
        elif " - pulad" in linha:  # aviso de etapa pulada: fica fora da tabela anterior
            fechar()
            titulo, linhas = None, [linha]
        else:
            linhas.append(linha)
    fechar()
    return partes


md = [f"# Execução do pipeline\n\nGerado por `src/executar_tudo.py` em {datetime.now():%d/%m/%Y %H:%M}. "
      "Base: NTSB (avall, 2008 a 2026).\n"]
for etapa in ETAPAS:
    print(f"\n{'=' * 20} {etapa} {'=' * 20}", flush=True)
    r = subprocess.run([sys.executable, etapa], cwd=SRC, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    md.append(f"## {etapa}\n")
    md += para_markdown(r.stdout)
    if r.returncode:
        md.append(f"**Erro (código {r.returncode}):**\n\n```text\n{r.stderr.strip()}\n```\n")
        SAIDA.write_text("\n".join(md), encoding="utf-8")
        sys.exit(r.returncode)
SAIDA.write_text("\n".join(md), encoding="utf-8")
print(f"\nSaída gravada em {SAIDA}")

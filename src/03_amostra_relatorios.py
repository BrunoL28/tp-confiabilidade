"""Etapa 3 - Relatórios finais do CENIPA: sorteio e planilha padronizada (Seção IV-A).

    python src/03_amostra_relatorios.py                # sorteia e cria a planilha
    python src/03_amostra_relatorios.py --baixar-pdfs  # também baixa os PDF e sugere um pré-preenchimento
    python src/03_amostra_relatorios.py --baixar-pdfs /mnt/c/Users/<voce>/Downloads   # usa PDF salvos no navegador

Todos os relatórios de turboélice e de jato entram; dos de pistão, sorteia-se uma amostra aleatória
simples com a semente de config/parametros.yaml. A planilha (data/processed/planilha_relatorios.xlsx)
é preenchida à mão; a etapa 5 a lê.
Se a planilha já existir, ela NÃO é sobrescrita (o preenchimento é preservado).
"""
import re
import sys

import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from comum import BRUTO, CONFIG, MOTORES, PROC, parametros

PLANILHA = PROC / "planilha_relatorios.xlsx"
PREENCHER = ["modelo_motor", "tsn_h", "tso_h", "componente", "bloco_rbd", "modo_falha", "origem",
             "so_operacional", "observacoes"]
ORIGENS = ["projeto", "fabricacao", "manutencao", "operacao", "indeterminado"]


def blocos_validos():
    """Valores aceitos em bloco_rbd, por motor: blocos em série + nome do par redundante."""
    b = pd.read_csv(CONFIG / "blocos_rbd.csv")
    b["valor"] = b["grupo"].where(b["estrutura"] == "paralelo", b["bloco"])
    return {m: list(dict.fromkeys(b.loc[b["motor"] == m, "valor"])) + ["indeterminado", "fora_do_modelo"]
            for m in MOTORES}


def sortear():
    p = parametros()
    pp = pd.read_csv(PROC / "cenipa_scf_pp.csv")
    rel = pp[pp["tem_relatorio"]].sort_values("codigo_ocorrencia")  # ordem fixa antes do sorteio
    rng = np.random.default_rng(p["semente_amostra"])
    pist = rel[rel["motor"] == "pistao"]
    idx = rng.choice(len(pist), size=min(p["tamanho_amostra_pistao"], len(pist)), replace=False)
    am = pd.concat([pist.iloc[np.sort(idx)], rel[rel["motor"] != "pistao"]])
    links = pd.read_csv(BRUTO / "cenipa" / "links_relatorios.csv")
    am = am.merge(links[["numero", "pdf_pt"]], left_on="divulgacao_relatorio_numero", right_on="numero", how="left")
    am = am.rename(columns={"divulgacao_relatorio_numero": "relatorio", "aeronave_matricula": "matricula",
                            "aeronave_modelo": "modelo_aeronave", "ocorrencia_classificacao": "classificacao",
                            "subtipo_scf_pp": "subtipo"})
    am["data"] = pd.to_datetime(am["data"]).dt.strftime("%d/%m/%Y")
    cols = ["codigo_ocorrencia", "motor", "relatorio", "data", "matricula", "modelo_aeronave", "n_motores",
            "classificacao", "subtipo", "pdf_pt"]
    am = am[cols].reset_index(drop=True)
    for c in PREENCHER:
        am[c] = ""
    print(f"Relatórios disponíveis: {rel.groupby('motor').size().to_dict()}")
    print(f"Na planilha: {am.groupby('motor').size().to_dict()} | semente {p['semente_amostra']} | "
          f"sem link de PDF: {int(am['pdf_pt'].isna().sum())}")
    return am


def gravar_planilha(am):
    validos = blocos_validos()
    with pd.ExcelWriter(PLANILHA, engine="openpyxl") as xw:
        am.to_excel(xw, sheet_name="relatorios", index=False)
        linhas = [(m, v) for m in MOTORES for v in validos[m]]
        pd.DataFrame(linhas, columns=["motor", "bloco_rbd"]).to_excel(xw, sheet_name="blocos_validos", index=False)
        pd.DataFrame({"campo": [
            "modelo_motor", "tsn_h / tso_h", "componente", "bloco_rbd", "modo_falha", "origem", "so_operacional"],
            "como preencher": [
            "modelo do motor que falhou, como no relatório (ex.: IO-540-K1J5)",
            "horas totais e desde a última revisão geral do motor; deixe vazio se o relatório não informa",
            "componente que falhou, em texto livre",
            "um valor da aba blocos_validos para o motor da linha; 'indeterminado' se a causa não foi identificada",
            "texto curto (fadiga, desgaste, vazamento, travamento, contaminação...)",
            "projeto, fabricacao, manutencao, operacao ou indeterminado",
            "S se a falha foi só operacional (ex.: esgotamento de combustível): é contada à parte"]}
        ).to_excel(xw, sheet_name="instrucoes", index=False)
    wb = load_workbook(PLANILHA)
    ws = wb["relatorios"]
    cab = {c.value: c.column_letter for c in ws[1]}
    n = ws.max_row
    todos = sorted({v for vs in validos.values() for v in vs})
    wsb = wb["blocos_validos"]
    wsb["D1"] = "todos"
    for i, v in enumerate(todos, start=2):
        wsb[f"D{i}"] = v
    faixa = f"=blocos_validos!$D$2:$D${len(todos) + 1}"
    dv = DataValidation(type="list", formula1=faixa, allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{cab['bloco_rbd']}2:{cab['bloco_rbd']}{n}")
    for col, lista in (("origem", ORIGENS), ("so_operacional", ["S", "N"])):
        dv = DataValidation(type="list", formula1='"' + ",".join(lista) + '"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{cab[col]}2:{cab[col]}{n}")
    for c in ws[1]:
        c.font = Font(bold=True)
        if c.value in PREENCHER:
            c.fill = PatternFill("solid", fgColor="FFF2CC")  # colunas a preencher
        ws.column_dimensions[c.column_letter].width = max(12, min(40, len(str(c.value)) + 6))
    ws.freeze_panes = "D2"
    wb.save(PLANILHA)


# ---------- pré-preenchimento opcional a partir do texto dos PDF ----------
RE_HORAS = r"(\d{1,3}(?:\.\d{3})*|\d+)\s*(?:h(?:oras)?\b)"
K_TSO = r"(?:TSO|desde a (?:última )?revisão(?: geral)?)"
K_TSN = r"(?:TSN|totais|horas totais|desde nov[oa])"


def _rx(chave):  # aceita "812 horas desde a última revisão" e "TSO: 812 horas"
    return re.compile(rf"{RE_HORAS}[^.]{{0,60}}?{chave}|{chave}[^.\d]{{0,80}}?{RE_HORAS}", re.I | re.S)


RE_TSO, RE_TSN = _rx(K_TSO), _rx(K_TSN)
RE_MOTOR = re.compile(r"\b((?:T?S?I?G?O|IO|TIO|TSIO|GTSIO|AEIO|LTIO)-\d{3}(?:-[A-Z0-9]+)*|PT6[AT]-\d+[A-Z]*|"
                      r"TPE331-[\dA-Z-]+|PW1\d{2}[A-Z]?|CFM56-[\dA-Z/-]+|V25\d{2}-[A-Z]\d|CF34-[\dA-Z]+|M601[A-Z-\d]*)\b")


def sugerir(texto, motor):
    """Sugestões a conferir na leitura: modelo do motor, TSN, TSO e bloco com mais termos no texto."""
    def horas(rx):
        m = rx.search(texto)
        return (m.group(1) or m.group(2)).replace(".", "") if m else ""

    mm = RE_MOTOR.search(texto)
    kw = pd.read_csv(CONFIG / "palavras_chave.csv")
    kw = kw[kw["motores"].str.split("|").apply(lambda x: motor in x)]
    baixo = texto.lower()
    cont = {r.bloco: sum(baixo.count(t.lower()) for t in r.termos.split("|")) for r in kw.itertuples()}
    melhor = max(cont, key=cont.get) if cont and max(cont.values()) > 0 else ""
    return dict(sug_modelo_motor=mm.group(1) if mm else "", sug_tsn_h=horas(RE_TSN), sug_tso_h=horas(RE_TSO),
                sug_bloco=melhor, sug_termos=str({k: v for k, v in sorted(cont.items(), key=lambda kv: -kv[1])[:3]}))


def baixar_e_sugerir(downloads=None):
    import html
    import shutil
    from pathlib import Path

    import pdfplumber
    import requests

    pasta = BRUTO / "cenipa" / "relatorios"
    pasta.mkdir(parents=True, exist_ok=True)
    am = pd.read_excel(PLANILHA, sheet_name="relatorios", dtype=str).fillna("")
    linhas, faltam = [], []
    for r in am.itertuples():
        destino = pasta / (re.sub(r"[^\w-]", "_", r.relatorio) + ".pdf")
        # PDF salvo pelo navegador mantém o nome do link; copia e renomeia
        salvo = Path(downloads) / r.pdf_pt.rsplit("/", 1)[-1] if downloads and r.pdf_pt else None
        if not destino.exists() and salvo and salvo.exists() and salvo.read_bytes()[:4] == b"%PDF":
            shutil.copyfile(salvo, destino)
        sug = {}
        try:
            if not destino.exists() and r.pdf_pt:
                resp = requests.get(r.pdf_pt, timeout=120)
                resp.raise_for_status()
                if not resp.content.startswith(b"%PDF"):
                    raise ValueError("resposta não é PDF (o site pode exigir abrir pelo navegador)")
                destino.write_bytes(resp.content)
            if destino.exists():
                with pdfplumber.open(destino) as pdf:
                    texto = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
                sug = sugerir(texto, r.motor)
        except Exception as e:
            sug = {"sug_termos": f"ERRO: {e}"}
        if not destino.exists():
            faltam.append(r)
        linhas.append({"codigo_ocorrencia": r.codigo_ocorrencia, "relatorio": r.relatorio, **sug})
    saida = PROC / "sugestoes_relatorios.csv"
    pd.DataFrame(linhas).to_csv(saida, index=False)
    print(f"Sugestões em {saida}. São ponto de partida para a leitura, não substituem a classificação manual.")
    if faltam:
        pagina = PROC / "pdfs_faltando.html"
        itens = "".join(f'<li><a href="{html.escape(r.pdf_pt)}">{html.escape(r.relatorio)}</a></li>' if r.pdf_pt
                        else f"<li>{html.escape(r.relatorio)}: sem link, procure no site do CENIPA</li>" for r in faltam)
        pagina.write_text(f"<meta charset=utf-8><h3>{len(faltam)} relatórios a baixar</h3><ol>{itens}</ol>",
                          encoding="utf-8")
        print(f"Faltam {len(faltam)} PDF. Abra {pagina} no navegador, clique em cada link (salva em Downloads) e rode:")
        print("  python src/03_amostra_relatorios.py --baixar-pdfs <pasta Downloads>")


if __name__ == "__main__":
    if PLANILHA.exists():
        print(f"{PLANILHA.name} já existe e foi mantida (apague-a para sortear de novo).")
    else:
        gravar_planilha(sortear())
        print(f"Planilha criada: {PLANILHA}")
    if "--baixar-pdfs" in sys.argv:
        i = sys.argv.index("--baixar-pdfs")
        baixar_e_sugerir(sys.argv[i + 1] if len(sys.argv) > i + 1 else None)

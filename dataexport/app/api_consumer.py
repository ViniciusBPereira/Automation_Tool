import os
import requests
from typing import List, Dict

from dataexport.app.logger import logger
from dataexport.app.models import Tarefa, Checklist


# === Configurações ===
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN não configurado no ambiente!")

BASE_URL_TAREFAS = "https://apiprod.gpsvista.com.br/api/planejamento/grid/tarefas"
URL_CHECKLIST = "https://apiprod.gpsvista.com.br/api/operacao/listar-por-tarefaId?tarefaId={}"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def build_payload(cr: str, nome: str) -> Dict:
    """Monta o payload dinâmico para buscar tarefas."""
    return {
        "value": {
            "requiresCounts": True,
            "where": [
                {
                    "isComplex": True,
                    "ignoreAccent": False,
                    "condition": "and",
                    "predicates": [
                        {"isComplex": False, "field": "CR", "operator": "contains", "value": cr, "ignoreCase": True, "ignoreAccent": False},
                        {"isComplex": False, "field": "Nome", "operator": "contains", "value": nome, "ignoreCase": True, "ignoreAccent": False}
                    ]
                }
            ],
            "sorted": [{"name": "Numero", "direction": "descending"}]
        }
    }



# === Funções principais ===
def fetch_tarefas(mes:str,cr:str,nome:str) -> List[Tarefa]:
    """Busca a lista de tarefas via API."""
    logger.info("Searching for tasks...")
    
    URL_TAREFAS = f"{BASE_URL_TAREFAS}?StatusFinalizada=true&Disponibilizacao_yyyyMM={mes}"
    PAYLOAD = build_payload(cr,nome)
    
    try:
        resp = requests.post(URL_TAREFAS, headers=HEADERS, json=PAYLOAD, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        tarefas = [Tarefa(**item) for item in data.get("result", [])]
        logger.info(f"{len(tarefas)} tasks received...")
        return tarefas
    except Exception:
        logger.error("Erro ao buscar tarefas", exc_info=True)
        return []


def fetch_checklist(tarefas: List[Tarefa]) -> List[Dict]:
    """Busca os checklists das tarefas recebidas."""
    resultados: List[Checklist] = []

    for t in tarefas:
        url = URL_CHECKLIST.format(t.Id)
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            checklist_items = resp.json()

            for item in checklist_items:
                resultados.append(Checklist(
                    tarefaId=t.Id,
                    nome=t.Nome,
                    local=t.Local,
                    data=t.TerminoReal,
                    recursonome=item.get("recursonome"),
                    tipo=item.get("tipo"),
                    perguntadescricao=item.get("perguntadescricao"),
                    conteudo=item.get("conteudo")
                ))
            
        except Exception:
            logger.error(f"Erro ao buscar checklist da tarefa {t.Id}", exc_info=True)
    return [r.model_dump() for r in resultados]


def run_pipeline(mes: str, cr: str, nome: str) -> List[Dict]:
    """Executa o fluxo completo: tarefas -> checklists -> JSON final."""
    tarefas = fetch_tarefas(mes,cr,nome)
    if not tarefas:
        logger.warning("Nenhuma tarefa encontrada.")
        return []
    return fetch_checklist(tarefas)



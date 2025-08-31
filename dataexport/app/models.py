from pydantic import BaseModel
from typing import Optional

class Tarefa(BaseModel):
    Id: str
    Local: str
    TerminoReal: str

class Checklist(BaseModel):
    tarefaId: str
    local: str
    data: str
    recursonome: Optional[str]
    tipo: Optional[int]
    perguntadescricao: Optional[str]
    conteudo: Optional[str]
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from dataexport.app.logger import logger
from dataexport.app.api_consumer import run_pipeline
from dataexport.app.excel_generator import generate_excel
import io
import re

app = FastAPI(title="DataExport")

@app.get("/data_export")
def gerar_excel(
    mes: str = Query(...),
    cr: str = Query(...),
    nome: str = Query(...)
):
    
    if not re.fullmatch(r"^\d{4}-(0[1-9]|1[0-2])$", mes):
        raise HTTPException(
            status_code=400,
            detail="Parameter 'month' must be in the yyyy-MM format (2025-08)..."
        )
    
    try:
        logger.info(f"Starting export mes={mes}, cr={cr}, nome={nome}...")
        data = run_pipeline(mes=mes, cr=cr, nome=nome)

        output = io.BytesIO()
        generate_excel(data, output)
        output.seek(0)

        logger.info("Export completed...")
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=dados.xlsx"}
        )

    except Exception as e:
        logger.exception(f"Error generating excel: {e}")

        raise HTTPException(status_code=500, detail="Internal error generating excel...")

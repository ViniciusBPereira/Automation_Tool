import pandas as pd
from dataexport.app.logger import logger

def generate_excel(data, output_stream):
    if not data:
        logger.warning("No data to export...")
        return
    df = pd.DataFrame(data)
    df.rename(columns=lambda c: c.replace("_", "").title(), inplace=True)
    df = df[df['Perguntadescricao'].notna()]
    df = df[df['Tipo'] == 1]
    pivot_df = df.pivot_table(
        index=['Tarefaid','Recursonome','Local','Data','Nome','Tipo'],
        columns='Perguntadescricao',
        values='Conteudo',
        aggfunc='first'
    ).reset_index()
    pivot_df = pivot_df.drop(columns=['Tarefaid'])
    pivot_df = pivot_df.drop(columns=['Tipo'])
    pivot_df.to_excel(output_stream, index=False)

    logger.info("Excel generated...")


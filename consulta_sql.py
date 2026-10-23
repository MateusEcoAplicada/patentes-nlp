import pandas as pd
import pandas_gbq
import os
from pathlib import Path

arquivo_credencial = Path(__file__).with_name(
  'iti-unesp-510015-1b5281550d01.json'
)
os.environ.setdefault(
  'GOOGLE_APPLICATION_CREDENTIALS',
  str(arquivo_credencial)
)
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'iti-unesp-510015')

query_teste = """
SELECT 
  publication_number,
  (SELECT text FROM UNNEST(title_localized) LIMIT 1) AS title,
  (SELECT text FROM UNNEST(abstract_localized) LIMIT 1) AS abstract,
  (SELECT text FROM UNNEST(claims_localized) LIMIT 1) AS claims, 
  
  PARSE_DATE('%Y%m%d', CAST(publication_date AS STRING)) AS publication_date

FROM 
  `patents-public-data.patents.publications`
WHERE 
  country_code = 'BR'
  AND publication_date >= 20110101
ORDER BY publication_date DESC
LIMIT 1000000
"""

# Baixando os dados
df_patentes = pandas_gbq.read_gbq(
    query_teste,
    project_id=project_id,
    dialect='standard'
)

# IMPORTANTE: Não use o dropna() nesta etapa de teste para vermos os dados brutos
# df_patentes = df_patentes.dropna(...)

print(df_patentes.info())
print(df_patentes.head())

df_patentes.to_csv('patentes_adquiridas_via_sql.csv', index=False)
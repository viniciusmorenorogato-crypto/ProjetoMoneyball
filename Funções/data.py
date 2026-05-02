import pandas as pd
import numpy as np  

def limpar_data_contrato(texto_data):
    """
    Converte uma data de contrato em texto para um valor decimal (Ano + Mês/12).
    Ex: '30/06/2026' ou 'Jun 2026' converte para 2026.5
    """
    if pd.isna(texto_data) or str(texto_data).strip() == '':
        return np.nan
    
    try:
        # O Pandas é inteligente e tenta traduzir o texto para uma data real.
        # dayfirst=True garante que ele entenda o padrão brasileiro (Dia/Mês/Ano)
        data = pd.to_datetime(texto_data, dayfirst=True)
        
        # Cria o número decimal: Ano + (Mês / 12)
        valor_numerico = data.year + (data.month / 12.0)
        
        return round(valor_numerico, 2)
        
    except Exception:
        # Caso a célula venha com um texto muito fora do padrão, retorna vazio
        return np.nan
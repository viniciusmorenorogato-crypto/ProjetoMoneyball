import pandas as pd
import numpy as np

def limpar_salario(texto_salario):
    """
    Limpa strings financeiras de salário, removendo '€', 'p/m', 'p/a', 'p/s',
    diferencia 'M' (milhão) de 'm' (milhar) e devolve o valor numérico (float).
    """
    if pd.isna(texto_salario) or str(texto_salario).strip() == '':
        return np.nan
    
    # Guarda o texto original para diferenciar maiúsculas e minúsculas
    texto_original = str(texto_salario).strip()
    
    # Remove o Euro, espaços e as variações de período (mês, ano, semana)
    texto_limpo = texto_original.replace('€', '').replace('p/m', '').replace('p/a', '').replace('p/s', '').replace(' ', '')
    
    multiplicador = 1
    
    # Diferencia M (Milhão) e m (Milhar) com precisão
    if 'M' in texto_limpo:
        multiplicador = 1_000_000
        texto_limpo = texto_limpo.replace('M', '')
    elif 'm' in texto_limpo or 'K' in texto_limpo or 'k' in texto_limpo:
        multiplicador = 1_000
        texto_limpo = texto_limpo.replace('m', '').replace('K', '').replace('k', '')
        
    # Troca vírgula por ponto para conversão matemática
    texto_limpo = texto_limpo.replace(',', '.')
    
    try:
        return float(texto_limpo) * multiplicador
    except ValueError:
        return np.nan

def limpar_valor_mercado(texto_valor):
    """
    Limpa strings financeiras, diferencia 'M' (milhão) de 'm' (milhar), 
    retorna a média e marca jogadores inegociáveis com -1.
    """
    if pd.isna(texto_valor) or str(texto_valor).strip() == '':
        return np.nan
    
    # Guarda o texto original sem alterar maiúsculas/minúsculas
    texto_original = str(texto_valor).strip()
    
    # 1. Checagem de inegociável (aqui criamos uma versão maiúscula só para comparar)
    texto_para_busca = texto_original.upper()
    if "NÃO ESTÁ À VENDA" in texto_para_busca or "NAO ESTA A VENDA" in texto_para_busca:
        return -1.0 
    
    # 2. Remove o Euro e espaços, mantendo o M e o m originais
    texto_limpo = texto_original.replace('€', '').replace(' ', '')
    partes = texto_limpo.split('-')
    valores_numericos = []
    
    for parte in partes:
        parte = parte.strip()
        multiplicador = 1
        
        # 3. Nova Regra: Diferencia M (Milhão) e m (Milhar) com precisão
        if 'M' in parte:
            multiplicador = 1_000_000
            parte = parte.replace('M', '')
        elif 'm' in parte:
            multiplicador = 1_000
            parte = parte.replace('m', '')
            
        parte = parte.replace(',', '.')
        
        try:
            valores_numericos.append(float(parte) * multiplicador)
        except ValueError:
            pass 
            
    if len(valores_numericos) == 2:
        return (valores_numericos[0] + valores_numericos[1]) / 2
    elif len(valores_numericos) == 1:
        return valores_numericos[0]
    else:
        return np.nan
import pandas as pd
import numpy as np

def limpar_valor_mercado(valor):
    if pd.isna(valor):
        return 0.0
        
    valor_str = str(valor).strip()
    
    # TRATATIVA 1: Inegociáveis (Mantida)
    if "NÃO ESTÁ" in valor_str.upper() or "INEGOCIÁVEL" in valor_str.upper():
        return -1.0
        
    # TRATATIVA 2: Valor Desconhecido (NOVA)
    if "DESCONHECIDO" in valor_str.upper():
        return -2.0

    # Limpeza visual (remove Euro e espaços)
    valor_str = valor_str.replace('€', '').replace(' ', '')
    
    def converter_numero(num_str):
        num_str = num_str.replace(',', '.')
        multiplicador = 1
        if 'M' in num_str:
            multiplicador = 1000000
            num_str = num_str.replace('M', '')
        elif 'm' in num_str:
            multiplicador = 1000
            num_str = num_str.replace('m', '')
        elif 'K' in num_str.upper() or 'k' in num_str.lower():
            multiplicador = 1000
            num_str = num_str.upper().replace('K', '')
        try:
            return float(num_str) * multiplicador
        except:
            return 0.0

    # TRATATIVA 3: Intervalos (Ex: 9,4M - 14M)
    if '-' in valor_str:
        partes = valor_str.split('-')
        val1 = converter_numero(partes[0])
        val2 = converter_numero(partes[1])
        return (val1 + val2) / 2.0
    else:
        # TRATATIVA 4: Valor Fixo (Antigo padrão)
        return converter_numero(valor_str)


def limpar_salario(salario):
    if pd.isna(salario):
        return 0.0
        
    salario_str = str(salario).strip()
    
    # NOVA TRATATIVA: Removemos as letras extras primeiro
    salario_str = salario_str.replace('€', '').replace('p/m', '').replace('p/a', '').replace('p/s', '').replace(' ', '')
    
    def converter_numero(num_str):
        num_str = num_str.replace(',', '.')
        multiplicador = 1
        if 'M' in num_str:
            multiplicador = 1000000
            num_str = num_str.replace('M', '')
        elif 'm' in num_str:
            multiplicador = 1000
            num_str = num_str.replace('m', '')
        elif 'K' in num_str.upper() or 'k' in num_str.lower():
            multiplicador = 1000
            num_str = num_str.upper().replace('K', '')
        try:
            return float(num_str) * multiplicador
        except:
            return 0.0

    # NOVA TRATATIVA: Intervalos de Salário (Ex: 5,25m - 8,5m)
    if '-' in salario_str:
        partes = salario_str.split('-')
        val1 = converter_numero(partes[0])
        val2 = converter_numero(partes[1])
        return (val1 + val2) / 2.0
    else:
        # TRATATIVA ANTIGA: Salário Fixo
        return converter_numero(salario_str)
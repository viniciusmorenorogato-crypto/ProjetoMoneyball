🌟 Sobre o Projeto
O Projeto Moneyball é uma ferramenta de análise de dados (Data Analytics) construída em Python, desenvolvida para ajudar jogadores de Football Manager a encontrarem os melhores reforços com base em estatísticas reais, fugindo do viés das "estrelinhas" de reputação. O programa transforma dados brutos de planilhas em decisões esportivas fundamentadas.

Através de modelagem matemática, o projeto analisa atributos exportados do jogo e gera um ranking absoluto dos melhores alvos custo-benefício para o seu time.

⚙️ Funcionalidades Principais

Leitura Inteligente de Dados: O sistema separa os jogadores por abas de posições específicas (Goleiros, Zagueiros, Meias, Atacantes) para análises contextualizadas.


Data Cleaning Automatizado: Limpeza profunda de colunas de texto, removendo símbolos de Euro e convertendo abreviações de milhões e milhares diretamente para números absolutos.


Tratamento de Contratos: Transforma datas de fim de contrato (Mês e Ano) em valores matemáticos contínuos de Ano Decimal para facilitar a análise de mercado.


Motor de Decisão (Método AHP): Aplica o Método Analytic Hierarchy Process com a Matriz de Saaty para definir pesos matemáticos exatos para cada critério escolhido.


Normalização Estatística (Min-Max): Equilibra atributos numéricos com naturezas opostas, penalizando estatísticas de "Custo" (como valores altos ou falhas) e premiando "Benefícios" (como defesas e notas médias).


Interface Web Interativa: Frontend moderno e responsivo construído com a biblioteca Streamlit, permitindo o uso da ferramenta diretamente pelo navegador sem precisar tocar no código.

🛠️ Tecnologias Utilizadas
Python: Linguagem base do projeto.

Pandas & NumPy: Extração, limpeza e processamento matricial dos dados exportados.

Streamlit: Criação da interface gráfica visual e interativa.

🤝 Agradecimentos e Créditos
Este projeto ganha vida graças à comunidade apaixonada de Football Manager. Um agradecimento especial e todos os créditos ao Allan FCL por disponibilizar a planilha base espetacular que a comunidade utiliza para extrair e organizar os dados de dentro do jogo. Sem esse trabalho fundamental, a aplicação das nossas fórmulas não seria possível!

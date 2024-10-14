# 1 --- Importing necessary libraries
import streamlit as st
from PIL import Image

# 2 - Importing Images and Data Set
cs_img = Image.open("Assets/marca_cesar_school.png")
melbourne_img = Image.open("Assets/Melbourne.jpg")


sidebar = st.sidebar
header = st.container()
box01 = st.container()
box02 = st.container()


introducao = """
- DataSet: [Link to Data Set](https://www.kaggle.com/datasets/dansbecker/melbourne-housing-snapshot?select=melb_data.csv)

Nos últimos anos, a crescente disponibilidade de dados e o avanço das tecnologias de análise de dados têm transformado diversos setores, 
incluindo o mercado imobiliário. A criação de aplicações que utilizam esses dados para gerar insights e previsões tem se mostrado uma 
ferramenta poderosa para diferentes stakeholders, desde compradores e vendedores de imóveis até profissionais do setor imobiliário. 

Este trabalho de conclusão de curso apresenta o desenvolvimento de uma aplicação DashBoard que analisa as principais características 
de imóveis na cidade de Melbourne, na Austrália, volume e seu preço de venda ao longo de uma série histórica dando a possibilidade do 
usuário filtrar sua pesquisa por diversos parâmetros. 
"""

aplicacao01 = """
A aplicação permite visualizar as tendências de preços de imóveis ao longo do tempo, identificando picos e quedas, 
bem como padrões sazonais. Isso ajuda os usuários a entenderem a dinâmica do mercado e a fazer previsões informadas sobre futuras variações 
de preços. 

Analisar quais características dos imóveis (como número de quartos, localização, área total, etc.) têm maior impacto no preço de venda pode 
orientar tanto compradores quanto vendedores na avaliação de propriedades.
"""

aplicacao02 = """
Os compradores de imóveis podem usar a aplicação para identificar áreas e tipos de propriedades que oferecem o melhor valor pelo seu dinheiro. 
Além disso, podem comparar preços históricos e estimar o valor futuro de um imóvel, ajudando na negociação e na decisão de compra. 

Os vendedores podem determinar o melhor momento para vender com base em análises históricas de preços e tendências de mercado. Isso pode 
maximizar o retorno sobre o investimento e acelerar o processo de venda.
"""
aplicacao03 = """
Investidores podem usar a aplicação para identificar oportunidades de investimento, avaliando áreas com maior potencial de valorização e 
propriedades subvalorizadas. Análises detalhadas ajudam na mitigação de riscos e na maximização dos retornos.

Autoridades e planejadores urbanos podem utilizar os dados e as análises para entender melhor o desenvolvimento do mercado imobiliário e 
planejar intervenções estratégicas que promovam um crescimento equilibrado e sustentável da cidade
"""

aplicacao04 = """
Os diversos filtros fornecidos juntos aos gráficos interativos fornece uma ferramenta poderosa para compradores e vendedores 
avaliarem rapidamente o valor de uma propriedade.
"""

dicionario_dados = """
- Price: Preço em Dólares
- Type: Tipo Acomodação
- Date: Data de Venda
- Distance: Distancia do Centro
- Regionname: Região
- Propertycount: Número de propriedades no bairro.
- Rooms : Quartos
- Bathroom: Banheiros
- Car: Vagas para Automóveis
- Landsize: Área do Terreno
- BuildingArea: Área Cosntruída
- YearBuilt: Ano de Cosntruçao
- Adress: Endereço do Imóvel
- Suburb: Bairro
"""

with sidebar:
    st.subheader("Dicionário de Dados")
    st.markdown(dicionario_dados)

with header:
    st.image(melbourne_img)
    st.title("Habitação em Melbourne (AUS)")


with box01:
    st.header("Problema de Negócio")
    st.markdown(introducao)
    st.header("Aplicações Práticas")
    st.subheader("1. Análise de Mercado")
    st.markdown(aplicacao01)
    st.subheader("2. Tomada de Decisão Informada")
    st.markdown(aplicacao02)
    st.subheader("3. Planejamento e Investimento")
    st.markdown(aplicacao03)
    st.subheader("4. Estimativa de Preço Inteligente")
    st.markdown(aplicacao04)

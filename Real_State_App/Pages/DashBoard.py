# 1 --- Importe as bibliotecas necessárias
import os
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import boto3
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('AWS_ACCESS_KEY_ID')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
default_region = os.getenv('AWS_DEFAULT_REGION')

# O bucket S3 onde o resultado da consulta será armazenado
S3_BUCKET = 'athena-result-bucket-tbat'
# A localização de saída dos resultados da consulta
S3_OUTPUT_LOCATION = f's3://{S3_BUCKET}/'

# Inicializando o cliente Boto3 para o Athena
athena_client = boto3.client(
    'athena',
    region_name=default_region,
    aws_access_key_id=api_key,
    aws_secret_access_key=secret_key
)


def execute_query(query):
    """
    Executa uma consulta SQL no Athena e retorna o resultado como um DataFrame do pandas.
    """
    response = athena_client.start_query_execution(
        QueryString=query,
        # Nome do seu database Athena
        QueryExecutionContext={'Database': 'real_state_sales_db'},
        ResultConfiguration={'OutputLocation': S3_OUTPUT_LOCATION}
    )

    # Obtenha o ID da execução da consulta
    query_execution_id = response['QueryExecutionId']

    # Aguarde a conclusão da consulta
    while True:
        query_status = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id)
        status = query_status['QueryExecution']['Status']['State']

        if status == 'SUCCEEDED':
            break
        elif status in ['FAILED', 'CANCELLED']:
            st.error(f"Query {status}")
            return None
        else:
            time.sleep(2)

    # Obtenha o resultado da consulta como um DataFrame
    result = athena_client.get_query_results(
        QueryExecutionId=query_execution_id)
    columns = [col['Label']
               for col in result['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [
        [value.get('VarCharValue', '') for value in row['Data']]
        for row in result['ResultSet']['Rows'][1:]
    ]

    df = pd.DataFrame(rows, columns=columns)
    return df

# Função para carregar dados iniciais


@st.cache_data
def load_filter_data():
    query = "SELECT Suburb, Regionname, Landsize FROM real_state_sales_table"
    return execute_query(query)


# Dados básicos aos Filtros
filter_dataset = load_filter_data()
if filter_dataset is not None:
    options_landsize = sorted(filter_dataset['Landsize'].dropna().unique())
else:
    st.error("Erro ao carregar os dados.")
    options_landsize = [200.0, 300.0, 400.0, 500.0, 600.0]


bHeader = st.container()
bSidebar = st.sidebar
bBox1, bBox2 = st.columns([1, 1])
bBox3 = st.container()
bBox4, bBox5 = st.columns([1, 1])


with bSidebar:
    st.title("Filtros de Consulta")
    # editar a sidebar
    suburb_filter = st.selectbox('Bairro:', list(
        filter_dataset.Suburb.unique()), placeholder="Choose an option", index=None)

    room_filter = st.slider("N* de Quartos:", min_value=1,
                            max_value=10, step=1)

    bath_filter = st.radio("N* de Banheiros:", ['0', '1', '2', '3', '4+', 'None'],
                           index=1, horizontal=True)

    region_filter = st.selectbox('Região:', list(
        filter_dataset.Regionname.unique()), placeholder="Choose an option", index=None)

    car_filter = st.radio("Vagas de Estacionamento:", ['0', '1', '2', '3', '4+', 'None'],
                          index=1, horizontal=True)

    start_landsize_filter, end_landsize_filter = st.select_slider("Área do Terreno:",
                                                                  options=options_landsize,
                                                                  value=(options_landsize[0], options_landsize[-1]))

    # Query base
    sql_query = "SELECT * FROM real_state_sales_table WHERE "
    sqlConector = ""

    # Bairro
    if (suburb_filter is not None):
        sql_query = sql_query + sqlConector + \
            f"""Suburb = '{suburb_filter}'"""
        sqlConector = " AND "

    # Região
    if (region_filter is not None):
        sql_query = sql_query + sqlConector + \
            f"""Regionname = '{region_filter}'"""
        sqlConector = " AND "

    # Banheiros
    if (bath_filter != 'None' and bath_filter != '4+'):
        sql_query = sql_query + sqlConector + \
            f"""CAST(Bathroom AS DOUBLE) = {bath_filter}"""
        sqlConector = " AND "
    elif (bath_filter != 'None' and bath_filter == '4+'):
        sql_query = sql_query + sqlConector + \
            "CAST(Bathroom AS DOUBLE) >= 4"
        sqlConector = " AND "

    # Banheiros
    if (car_filter != 'None' and car_filter != '4+'):
        sql_query = sql_query + sqlConector + \
            f"""CAST(NULLIF(Car, '') AS DOUBLE) = {car_filter}"""
        sqlConector = " AND "
    elif (car_filter != 'None' and car_filter == '4+'):
        sql_query = sql_query + sqlConector + \
            "CAST(NULLIF(Car, '') AS DOUBLE) >= 4"
        sqlConector = " AND "

    # Área do Terreno + N* Quartos
    sql_query = sql_query + sqlConector + \
        f"""CAST(Landsize AS DOUBLE) BETWEEN {start_landsize_filter}
            AND {end_landsize_filter} AND
            CAST(Rooms AS DOUBLE) = {room_filter}"""


# Gera dados para Filtros de Inicialização
general_dataset = execute_query(sql_query)
general_dataset['price'] = pd.to_numeric(
    general_dataset['price'], errors='coerce')
general_dataset['date'] = pd.to_datetime(
    general_dataset['date'], errors='coerce', format='%d/%m/%Y')
general_dataset['date'] = general_dataset['date'].dt.strftime('%m/%Y')
general_dataset['lattitude'] = pd.to_numeric(
    general_dataset['lattitude'], errors='coerce')
general_dataset['longtitude'] = pd.to_numeric(
    general_dataset['longtitude'], errors='coerce')
general_dataset['price'] = pd.to_numeric(
    general_dataset['price'], errors='coerce')

with bBox1:

    st.header("Valor Médio Imóveis")

    dff01 = general_dataset.copy()
    # Group and order By Period
    dff01 = dff01.groupby('date')['price'].mean(
    ).reset_index(name='Average_Price')

    y_min = dff01['Average_Price'].min()
    y_max = dff01['Average_Price'].max()

    fig1 = px.line(dff01, x='date', y="Average_Price")
    fig1.update_traces(line=dict(color='orange'))
    fig1.update_yaxes(range=[y_min, y_max])
    st.plotly_chart(fig1, use_container_width=True)

with bBox2:

    st.header("Número de Vendas Mês a Mês")

    dff02 = general_dataset.copy()
    dff02 = dff02.groupby('date').size().reset_index(name='Sales')

    fig2 = px.bar(dff02, x='date', y='Sales', title='Monthly Sales')
    st.plotly_chart(fig2, use_container_width=True)


with bBox3:

    st.header("Preço Médio por Região ao Longo do Tempo")

    dff03 = general_dataset.copy()
    # Agrupar dados por Data e Região e calcular o preço médio
    dff03 = dff03.groupby(['date', 'regionname']).agg(
        {'price': 'mean'}).reset_index()

    # Criar o gráfico
    fig3 = px.scatter(dff03, x="date", y="price",
                      color="regionname", symbol="regionname", size='price',
                      labels={"price": "Preço Médio", "date": "Data"})
    st.plotly_chart(fig3, use_container_width=True)

with bBox4:

    st.header("Volume de Vendas em Melbourn por Regiao")
    dff04 = general_dataset.copy()
   # Agrupar por região e calcular a média das coordenadas
    df_grouped = dff04.groupby('regionname').agg({
        'lattitude': 'mean',
        'longtitude': 'mean',
        'price': 'count'  # Contar o número de registros
    }).reset_index()

    # Renomear a coluna 'Price' para 'Count' para representar o número de registros
    df_grouped.rename(columns={'price': 'Count'}, inplace=True)

    # Criar o gráfico Bubble Map
    fig4 = px.scatter_geo(df_grouped,
                          lat='lattitude',
                          lon='longtitude',
                          size='Count',  # Tamanho das bolhas baseado no número de registros
                          color='regionname',
                          hover_name='regionname',
                          size_max=50,
                          labels={"Count": "Total de Vendas"},
                          projection="natural earth"
                          )

    # Exibir o gráfico
    st.plotly_chart(fig4, use_container_width=True)

with bBox5:

    st.header("Bairro Campeão de Vendas Mês a Mês")

    dff05 = general_dataset.copy()

    # Agrupando por 'Date' e 'Suburb' e contando as entradas
    monthly_counts = dff05.groupby(
        ['date', 'suburb']).size().reset_index(name='Counts')

    # Encontrando o subúrbio com o maior número de registros em cada mês
    max_suburbs = monthly_counts.loc[monthly_counts.groupby(
        'date')['Counts'].idxmax()]

    # Criando o gráfico
    fig5 = px.bar(max_suburbs, x='date', y='Counts', color='suburb', text='suburb',
                  labels={'date': 'Mês', 'Counts': 'Número de Vendas', 'suburb': 'Bairro'})
    # Exibir o gráfico
    st.plotly_chart(fig5, use_container_width=True)

from pathlib import Path
from datetime import date, datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title= 'RESUMO GERAL', layout='wide')

COMISSAO = 0.08
COLUNAS_ANALISE = ['filial', 'vendedor', 'produto']
COLUNAS_NUMERICAS =  ['preco', 'comissao']
FUNCOES_AGG = {'soma': 'sum', 'contagem': 'count'}

pasta_datasets = Path(__file__).parent.parent / 'datasets'
df_vendas = pd.read_csv(pasta_datasets / 'vendas.csv', decimal=',', sep=';', index_col=0, parse_dates=True)
df_filiais = pd.read_csv(pasta_datasets / 'filiais.csv', decimal=',', sep=';', index_col=0)
df_produtos = pd.read_csv(pasta_datasets / 'produtos.csv', decimal=',', sep=';', index_col=0)

df_produtos = df_produtos.rename(columns={'nome': 'produto'})
df_vendas = df_vendas.reset_index()
df_vendas = pd.merge(left=df_vendas.reset_index(),
                     right=df_produtos[['preco', 'produto']],
                     on='produto',
                     how='left')
df_vendas = df_vendas.set_index('data')
df_vendas['comissao'] = df_vendas['preco'] * COMISSAO

data_inicial = st.sidebar.date_input('Data inicial', df_vendas.index.date.max() - timedelta(days=7))
data_final = st.sidebar.date_input('Data final', df_vendas.index.date.max())

df_vendas_corte = df_vendas[(df_vendas.index.date >= data_inicial) & (df_vendas.index.date <= data_final)]
valor_vendas = f"R${df_vendas_corte['preco'].sum():.2f}"
qnt_vendas = df_vendas_corte['preco'].count()

col11, col12, col13 = st.columns([0.5, 0.25, 0.25])
col11.markdown('# Numeros Gerais')
col12.metric('Valor de vendas no período', valor_vendas)
col13.metric('Quantidade de vendas no período', qnt_vendas)
st.divider()

col21, col22 = st.columns(2)

df_vendas_corte['dia_venda'] = df_vendas_corte.index.date
vendas_dia = df_vendas_corte.groupby('dia_venda').agg({'preco': 'sum'})
fig = px.line(vendas_dia)
col21.plotly_chart(fig)

analise_selecionada = st.sidebar.selectbox('Analisar:', COLUNAS_ANALISE)

fig = px.pie(df_vendas_corte, values='preco', names=analise_selecionada)
col22.plotly_chart(fig)

st.dataframe(df_vendas_corte)
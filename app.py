import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuracao da Pagina
st.set_page_config(page_title="TI - Walfredo Gurguel", layout="wide", page_icon="🏥")

# Cabecalho Oficial
st.markdown(f"""
    <div style="background-color:#003366;padding:20px;border-radius:10px">
    <h1 style="color:white;text-align:center;margin:0;">HOSPITAL MONSENHOR WALFREDO GURGUEL</h1>
    <p style="color:white;text-align:center;font-size:18px;margin:5px;">Producao de Tecnologia da Informacao (TI)</p>
    </div>
    """, unsafe_allow_html=True)

# LISTA DE SETORES (Sem acentos para evitar erros de busca/filtro)
SETORES = sorted([
    "ADM", "ALMOXARIFADO", "ARQUIVO", "ATENDIMENTO CLINICO", "BANCO DE SANGUE", 
    "CAF (CENTRAL DE ABASTECIMENTO FARMACEUTICO)", "CCIH", "CEDEQ", "CENTRAL DE MATERIAIS", 
    "CENTRAL TELEFONICA", "CENTRO CIRURGICO", "CEQUIP", "CLASSIFICACAO DE RISCO", 
    "CLINICA MEDICA", "CME", "COMISSAO DE CONTROLE INTERNO", "COMPRAS", "CONTRATOS", 
    "CONTRATOS SESAP (OPME)", "COORDENACAO DE ENFERMAGEM", "CRO (COMISSAO DE REVISAO DE OBITO)", 
    "CTQ (CENTRO DE TRATAMENTO DE QUEIMADOS)", "CUSTOS", "DEPTO DE ENFERMAGEM", "DIRECAO GERAL", 
    "DIRECAO OPERACIONAL", "DIRECAO ADMINISTRATIVA E FINANCEIRA", "DIRECAO ENFERMAGEM", 
    "DIV. FINANCEIRA", "DIV. GESTAO DE PESSOAS (RH)", "DIV. MATERIAIS", "DIV. NUTRICAO", 
    "DIV. SERVICOS GERAIS", "ECG", "EMNT", "ENDOSCOPIA", "EPIDEMIOLOGIA", "FARMACIA CENTRAL", 
    "FARMACIA CENTRO CIRURGICO", "FARMACIA PSCS", "FATURAMENTO", "GESTAO DE ALTA", "HEMODIALISE", 
    "HIGIENIZACAO", "LABORATORIO DE ANALISES CLINICAS", "LAVANDERIA", "MANUTENCAO", "NAQH", 
    "NAST", "NEP", "NHE", "NIR", "NSP", "NULIC", "NUVISA", "OBSERVACAO 2", "OPO", "ORTOPEDIA", 
    "OTORRINO/OFTALMO", "OUVIDORIA", "PATRIMONIO", "PEDIATRIA", "PLANTAO ADMINISTRATIVO PSCS", 
    "POLITRAUMA", "POSTO DE ENFERMAGEM 2o ANDAR", "POSTO DE ENFERMAGEM 3o ANDAR", 
    "POSTO DE ENFERMAGEM 4o ANDAR", "POSTO DE ENFERMAGEM 5o ANDAR", "PSICOLOGIA", "RAIO-X", 
    "REABILITACAO", "RECEPCAO PRINCIPAL/INTERNAMENTO", "RESIDENCIA MEDICA", "RPA", "SAD", "SADT", 
    "SALA DE GESSO", "SALA DE VACINA", "SAME", "SCIH", "SERVICO SOCIAL", "TI (TECNOLOGIA DA INFORMACAO)", 
    "TOMOGRAFIA", "UAVC", "UCI PSCS", "ULTRASSONOGRAFIA", "URGENCIA PEDIATRICA", "UTI GERAL 1", 
    "UTI GERAL 2", "UTI PEDIATRICA", "UTI RPAI"
])

TECNICOS = ["Thiago", "Italo", "Ulisses", "Katriel", "Luandson"]

# Conexao com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Menu de Navegacao
aba = st.sidebar.radio("Navegar por:", ["🚀 Registrar Chamado", "📊 Relatorio de Producao"])

# --- ABA 1: REGISTRO ---
if aba == "🚀 Registrar Chamado":
    st.subheader("📝 Lancar Novo Atendimento")
    
    with st.form("form_producao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tecnico = st.selectbox("Quem atendeu?", TECNICOS)
        with col2:
            setor = st.selectbox("Qual o setor?", SETORES)
            
        descricao = st.text_area("O que foi realizado?", placeholder="Ex: Manutencao de ponto de rede ou troca de computador.")
        
        btn_enviar = st.form_submit_button("✅ Salvar Producao")
        
        if btn_enviar

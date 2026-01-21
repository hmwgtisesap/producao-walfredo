import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuracao da Pagina
st.set_page_config(page_title="TI - Walfredo Gurguel", layout="wide", page_icon="🏥")

# Identidade Visual
st.markdown(f"""
    <div style="background-color:#003366;padding:20px;border-radius:10px">
    <h1 style="color:white;text-align:center;margin:0;">HOSPITAL MONSENHOR WALFREDO GURGUEL</h1>
    <p style="color:white;text-align:center;font-size:18px;margin:5px;">Producao de Tecnologia da Informacao (TI)</p>
    </div>
    """, unsafe_allow_html=True)

# Lista de Setores Padronizada
SETORES = sorted([
    "ADM", "ALMOXARIFADO", "ARQUIVO", "ATENDIMENTO CLINICO", "BANCO DE SANGUE", 
    "CAF", "CCIH", "CEDEQ", "CENTRAL DE MATERIAIS", "CENTRAL TELEFONICA", "CENTRO CIRURGICO", 
    "CEQUIP", "CLASSIFICACAO DE RISCO", "CLINICA MEDICA", "CME", "COMPRAS", "CONTRATOS", 
    "CTQ", "DIRECAO GERAL", "DIV. FINANCEIRA", "DIV. GESTAO DE PESSOAS (RH)", "DIV. MATERIAIS", 
    "DIV. NUTRICAO", "DIV. SERVICOS GERAIS", "ECG", "EMNT", "EPIDEMIOLOGIA", "FARMACIA CENTRAL", 
    "FATURAMENTO", "HEMODIALISE", "LABORATORIO", "LAVANDERIA", "MANUTENCAO", "NIR", "NULIC", 
    "ORTOPEDIA", "OUVIDORIA", "PEDIATRIA", "POLITRAUMA", "RAIO-X", "SADT", "SAME", 
    "SERVICO SOCIAL", "TI (TECNOLOGIA DA INFORMACAO)", "TOMOGRAFIA", "UAVC", "UCI", 
    "URGENCIA PEDIATRICA", "UTI GERAL 1", "UTI GERAL 2", "UTI PEDIATRICA"
])

TECNICOS = ["Thiago", "Italo", "Ulisses", "Katriel", "Luandson"]

# Conexao
conn = st.connection("gsheets", type=GSheetsConnection)

aba = st.sidebar.radio("Navegar por:", ["🚀 Registrar Chamado", "📊 Relatorio de Producao"])

if aba == "🚀 Registrar Chamado":
    st.subheader("📝 Lancar Novo Atendimento")
    
    with st.form("form_producao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tecnico = st.selectbox("Quem atendeu?", TECNICOS)
        with col2:
            setor = st.selectbox("Qual o setor?", SETORES)
            
        descricao = st.text_area("O que foi realizado?", placeholder="Ex: Manutencao de ponto de rede.")
        
        btn_enviar = st.form_submit_button("✅ Salvar Producao")
        
        if btn_enviar:
            if not descricao:
                st.warning("Por favor, descreva o servico.")
            else:
                agora = datetime.now()
                # DataFrame com nomes identicos aos cabecalhos da planilha
                novo_registro = pd.DataFrame([{
                    "Data": agora.strftime("%d/%m/%Y %H:%M"),
                    "Mes": agora.strftime("%m - %B"),
                    "Ano": agora.year,
                    "Tecnico": tecnico,
                    "Setor": setor,
                    "Descricao": descricao
                }])
                
                try:
                    # Tenta ler a aba Producao
                    df_atual = conn.read(worksheet="Producao")
                    df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                    conn.update(worksheet="Producao", data=df_final)
                    st.success("Atendimento registrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

else:
    st.subheader("📊 Resumo Mensal")
    try:
        df = conn.read(worksheet="Producao")
        if not df.empty:
            mes_f = st.selectbox("Selecione o Mes:", sorted(df['Mes'].unique()))
            df_mes = df[df['Mes'] == mes_f]
            st.metric("Total de Atendimentos", len(df_mes))
            st.bar_chart(df_mes['Setor'].value_counts())
            with st.expander("Detalhes"):
                st.table(df_mes['Tecnico'].value_counts().reset_index(name='Qtd'))
                st.dataframe(df_mes)
    except:
        st.info("Aguardando registros...")

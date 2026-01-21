import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuracao da Pagina
st.set_page_config(page_title="TI - Walfredo Gurguel", layout="wide", page_icon="🏥")

# Cabecalho com Identidade Visual do Hospital
st.markdown(f"""
    <div style="background-color:#003366;padding:20px;border-radius:10px">
    <h1 style="color:white;text-align:center;margin:0;">HOSPITAL MONSENHOR WALFREDO GURGUEL</h1>
    <p style="color:white;text-align:center;font-size:18px;margin:5px;">Producao de Tecnologia da Informacao (TI)</p>
    </div>
    """, unsafe_allow_html=True)

# LISTA DE SETORES DO LEVANTAMENTO HMWG (Sem acentos para evitar erros de banco de dados)
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

# Conexao com Google Sheets via Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# Menu Lateral
aba = st.sidebar.radio("Navegar por:", ["🚀 Registrar Chamado", "📊 Relatorio de Producao"])

# --- ABA 1: REGISTRO DE ATENDIMENTO ---
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
        
        if btn_enviar:
            if not descricao:
                st.warning("Por favor, descreva o servico.")
            else:
                agora = datetime.now()
                # Colunas padronizadas sem acento para casar com a planilha
                novo_registro = pd.DataFrame([{
                    "Data": agora.strftime("%d/%m/%Y %H:%M"),
                    "Mes": agora.strftime("%m - %B"),
                    "Ano": agora.year,
                    "Tecnico": tecnico,
                    "Setor": setor,
                    "Descricao": descricao
                }])
                
                try:
                    # Leitura e atualizacao da aba unica 'Producao'
                    df_atual = conn.read(worksheet="Producao")
                    df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                    conn.update(worksheet="Producao", data=df_final)
                    st.success(f"Atendimento no setor {setor} salvo com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}. Verifique se a aba se chama Producao e se o acesso e Editor.")

# --- ABA 2: RELATORIOS DE GESTAO ---
else:
    st.subheader("📊 Resumo de Producao Mensal")
    
    try:
        df = conn.read(worksheet="Producao")
        
        if not df.empty:
            lista_meses = sorted(df['Mes'].unique())
            mes_f = st.selectbox("Selecione o Mes para fechar a producao:", lista_meses)
            
            df_mes = df[df['Mes'] == mes_f]

            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Total de Atendimentos", len(df_mes))
            
            if not df_mes.empty:
                setor_max = df_mes['Setor'].value_counts().idxmax()
                qtd_setor_max = df_mes['Setor'].value_counts().max()
                c2.metric("Setor Mais Demandado", f"{setor_max} ({qtd_setor_max})")

            st.divider()
            st.write("### Ranking de Atendimentos por Setor")
            st.bar_chart(df_mes['Setor'].value_counts())
            
            with st.expander("Ver contagem por tecnico e dados detalhados"):
                st.table(df_mes['Tecnico'].value_counts().reset_index(name='Qtd'))
                st.dataframe(df_mes, use_container_width=True)
        else:
            st.info("Nenhum dado encontrado na planilha.")
    except Exception as e:
        st.info("Aguardando registros ou verifique a conexao com a planilha.")

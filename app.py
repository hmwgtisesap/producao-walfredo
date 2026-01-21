import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="TI - Walfredo Gurguel", layout="wide", page_icon="🏥")

# Cabeçalho Oficial
st.markdown(f"""
    <div style="background-color:#003366;padding:20px;border-radius:10px">
    <h1 style="color:white;text-align:center;margin:0;">HOSPITAL MONSENHOR WALFREDO GURGUEL</h1>
    <p style="color:white;text-align:center;font-size:18px;margin:5px;">Produção de Tecnologia da Informação (TI)</p>
    </div>
    """, unsafe_allow_html=True)

# LISTA DE SETORES (Formatada do seu levantamento)
SETORES = sorted([
    "ADM", "ALMOXARIFADO", "ARQUIVO", "ATENDIMENTO CLINICO", "BANCO DE SANGUE", 
    "CAF (CENTRAL DE ABASTECIMENTO FARMACÊUTICO)", "CCIH", "CEDEQ", "CENTRAL DE MATERIAIS", 
    "CENTRAL TELEFONICA", "CENTRO CIRURGICO", "CEQUIP", "CLASSIFICAÇÃO DE RISCO", 
    "CLINICA MEDICA", "CME", "COMISSÃO DE CONTROLE INTERNO", "COMPRAS", "CONTRATOS", 
    "CONTRATOS SESAP (OPME)", "COORDENAÇÃO DE ENFERMAGEM", "CRO (COMISSÃO DE REVISÃO DE ÓBITO)", 
    "CTQ (CENTRO DE TRATAMENTO DE QUEIMADOS)", "CUSTOS", "DEPTO DE ENFERMAGEM", "DIREÇÃO GERAL", 
    "DIREÇÃO OPERACIONAL", "DIREÇÃO ADMINISTRATIVA E FINANCEIRA", "DIREÇÃO ENFERMAGEM", 
    "DIV. FINANCEIRA", "DIV. GESTÃO DE PESSOAS (RH)", "DIV. MATERIAIS", "DIV. NUTRIÇÃO", 
    "DIV. SERVIÇOS GERAIS", "ECG", "EMNT", "ENDOSCOPIA", "EPIDEMIOLOGIA", "FARMACIA CENTRAL", 
    "FARMACIA CENTRO CIRURGICO", "FARMACIA PSCS", "FATURAMENTO", "GESTÃO DE ALTA", "HEMODIALISE", 
    "HIGIENIZACAO", "LABORATORIO DE ANALISES CLINICAS", "LAVANDERIA", "MANUTENÇÃO", "NAQH", 
    "NAST", "NEP", "NHE", "NIR", "NSP", "NULIC", "NUVISA", "OBSERVAÇÃO 2", "OPO", "ORTOPEDIA", 
    "OTORRINO/OFTALMO", "OUVIDORIA", "PATRIMONIO", "PEDIATRIA", "PLANTÃO ADMINISTRATIVO PSCS", 
    "POLITRAUMA", "POSTO DE ENFERMAGEM 2o ANDAR", "POSTO DE ENFERMAGEM 3o ANDAR", 
    "POSTO DE ENFERMAGEM 4o ANDAR", "POSTO DE ENFERMAGEM 5o ANDAR", "PSICOLOGIA", "RAIO-X", 
    "REABILITAÇÃO", "RECEPÇÃO PRINCIPAL/INTERNAMENTO", "RESIDENCIA MEDICA", "RPA", "SAD", "SADT", 
    "SALA DE GESSO", "SALA DE VACINA", "SAME", "SCIH", "SERVIÇO SOCIAL", "TI (TECNOLOGIA DA INFORMAÇÃO)", 
    "TOMOGRAFIA", "UAVC", "UCI PSCS", "ULTRASSONOGRAFIA", "URGENCIA PEDIATRICA", "UTI GERAL 1", 
    "UTI GERAL 2", "UTI PEDIATRICA", "UTI RPAI"
])

TECNICOS = ["Thiago", "Italo", "Ulisses", "Katriel", "Luandson"]

# Conexão com Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Erro na conexão com a planilha. Verifique as Secrets.")

# Menu de Navegação
aba = st.sidebar.radio("Navegar por:", ["🚀 Registrar Chamado", "📊 Relatório de Produção"])

# --- ABA 1: REGISTRO ---
if aba == "🚀 Registrar Chamado":
    st.subheader("📝 Lançar Novo Atendimento")
    
    with st.form("form_producao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tecnico = st.selectbox("Quem atendeu?", TECNICOS)
        with col2:
            setor = st.selectbox("Qual o setor?", SETORES)
            
        descricao = st.text_area("O que foi realizado?", placeholder="Ex: Manutenção de ponto de rede ou troca de computador.")
        
        btn_enviar = st.form_submit_button("✅ Salvar Produção")
        
        if btn_enviar:
            if not descricao:
                st.warning("Por favor, descreva o serviço.")
            else:
                agora = datetime.now()
                novo_registro = pd.DataFrame([{
                    "Data": agora.strftime("%d/%m/%Y %H:%M"),
                    "Mês": agora.strftime("%m - %B"),
                    "Ano": agora.year,
                    "Técnico": tecnico,
                    "Setor": setor,
                    "Descrição": descricao
                }])
                
                try:
                    df_atual = conn.read(worksheet="Producao")
                    df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                    conn.update(worksheet="Producao", data=df_final)
                    st.success(f"Atendimento no setor {setor} computado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

# --- ABA 2: RELATÓRIOS ---
else:
    st.subheader("📊 Produção Mensal")
    
    try:
        df = conn.read(worksheet="Producao")
        
        if not df.empty:
            # Filtros
            lista_meses = sorted(df['Mês'].unique())
            mes_f = st.selectbox("Selecione o Mês para fechar a produção:", lista_meses)
            
            df_mes = df[df['Mês'] == mes_f]

            # Indicadores Principais
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Total de Atendimentos", len(df_mes))
            
            if not df_mes.empty:
                setor_max = df_mes['Setor'].value_counts().idxmax()
                qtd_setor_max = df_mes['Setor'].value_counts().max()
                c2.metric("Setor Mais Atendido", f"{setor_max} ({qtd_setor_max})")

            st.divider()
            
            # Gráfico de Setores
            st.write("### Ranking de Atendimentos por Setor")
            st.bar_chart(df_mes['Setor'].value_counts())
            
            # Tabela de técnicos discreta (Contagem)
            with st.expander("Ver contagem por técnico (Equipe)"):
                st.table(df_mes['Técnico'].value_counts().reset_index(name='Qtd'))
                st.write("### Dados Detalhados")
                st.dataframe(df_mes, use_container_width=True)
                
        else:
            st.info("Nenhum dado encontrado na aba 'Producao'.")
    except Exception as e:
        st.info("Aguardando dados ou verifique se a aba 'Producao' existe na planilha.")

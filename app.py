import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import traceback

# 1. CONFIGURAÇÕES E CONEXÃO
st.set_page_config(page_title="TI - Walfredo Gurguel", layout="wide", page_icon="🏥")

# Conexão oficial via Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. LISTAS COMPLETAS (Com opção em branco no início)
# Adicionamos o "" no início para que o selectbox comece vazio
TECNICOS = [""] + ["Thiago", "Italo", "Ulisses", "Katriel", "Luandson"]

SETORES = [""] + sorted([
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

# 3. INTERFACE LATERAL
aba = st.sidebar.radio("Menu:", ["🚀 Registrar Atividade", "📊 Relatório Mensal"])

if aba == "🚀 Registrar Atividade":
    st.subheader("📝 Lançar Novo Atendimento")
    
    with st.form("form_dados", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tecnico = st.selectbox("Quem atendeu?", TECNICOS)
        with col2:
            setor = st.selectbox("Qual o setor?", SETORES)
            
        data_servico = st.date_input("Data do Serviço", datetime.now())
        descricao = st.text_area("O que foi realizado?", placeholder="Ex: Manutenção de ponto de rede.")
        
        btn_enviar = st.form_submit_button("✅ Salvar na Planilha")
        
        if btn_enviar:
            # Validação para garantir que nada seja enviado vazio
            if tecnico == "" or setor == "":
                st.error("⚠️ Por favor, selecione o Técnico e o Setor.")
            elif not descricao:
                st.warning("⚠️ Por favor, descreva o serviço realizado.")
            else:
                try:
                    # Lê a base atual para fazer o append (não sobrescrever)
                    df_atual = conn.read(worksheet="dados", ttl=0)
                    
                    # Prepara a nova linha
                    nova_linha = pd.DataFrame([{
                        "Data": data_servico.strftime("%d/%m/%Y"),
                        "Mes": data_servico.strftime("%m - %B"),
                        "Ano": data_servico.year,
                        "Tecnico": tecnico,
                        "Setor": setor,
                        "Descricao": descricao
                    }])
                    
                    # Une os dados
                    df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                    
                    # Envia para a planilha (Requer Service Account como EDITOR)
                    conn.update(worksheet="dados", data=df_final)
                    st.success("✅ Atendimento registrado com sucesso!")
                    
                except Exception:
                    st.error("❌ Erro ao salvar. Verifique os logs:")
                    st.code(traceback.format_exc())

else:
    st.subheader("📊 Resumo de Produção")
    try:
        df = conn.read(worksheet="dados", ttl=0)
        
        if not df.empty:
            # Filtro de Mês começando em branco para não carregar tudo de vez
            meses = [""] + sorted(df['Mes'].unique().tolist(), reverse=True)
            mes_f = st.selectbox("Selecione o Mês:", meses)
            
            if mes_f != "":
                df_mes = df[df['Mes'] == mes_f]
                
                # Métricas e Gráficos
                c1, c2 = st.columns(2)
                c1.metric("Total de Atendimentos", len(df_mes))
                
                st.write(f"### Atendimentos por Setor em {mes_f}")
                st.bar_chart(df_mes['Setor'].value_counts())
                
                with st.expander("Ver Detalhes dos Chamados"):
                    st.dataframe(df_mes, use_container_width=True)
            else:
                st.info("Selecione um mês para visualizar o relatório.")
        else:
            st.info("Aguardando os primeiros registros na planilha...")
            
    except Exception:
        st.error("Erro ao carregar o relatório.")
        st.code(traceback.format_exc())

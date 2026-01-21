import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import traceback

# 1. CONFIGURAÇÕES INICIAIS
st.set_page_config(page_title="TI - Produção Hospitalar", layout="wide")

# Conexão (Busca automaticamente do secrets.toml ou do painel do Streamlit Cloud)
conn = st.connection("gsheets", type=GSheetsConnection)

# Listas auxiliares
SETORES = sorted(["ADM", "ALMOXARIFADO", "CENTRO CIRURGICO", "TI", "UTI GERAL", "PRONTO SOCORRO", "SAME", "FARMACIA"])
TECNICOS = ["Thiago", "Italo", "Ulisses", "Katriel", "Luandson"]

# 2. INTERFACE
st.title("🏥 Sistema de Produção de TI")
aba = st.sidebar.radio("Menu", ["Registrar Atividade", "Relatório Mensal"])

if aba == "Registrar Atividade":
    st.header("🚀 Nova Atividade")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tecnico = st.selectbox("Técnico", TECNICOS)
            setor = st.selectbox("Setor", SETORES)
        with col2:
            data_manual = st.date_input("Data do Serviço", datetime.now())
            
        descricao = st.text_area("Descrição do Serviço (Pode repetir 'teste' se necessário)")
        
        btn_salvar = st.form_submit_button("Salvar na Planilha")

        if btn_salvar:
            if not descricao:
                st.warning("Preencha a descrição.")
            else:
                try:
                    # --- O PULO DO GATO PARA NÃO SOBRESCREVER ---
                    # Lemos a planilha inteira primeiro (ttl=0 é vital aqui)
                    df_antigo = conn.read(worksheet="dados", ttl=0)
                    
                    # Criamos a linha nova
                    agora = datetime.now()
                    nova_linha = pd.DataFrame([{
                        "Data": data_manual.strftime("%d/%m/%Y"),
                        "Mes": data_manual.strftime("%m - %B"), # Ex: 01 - January
                        "Ano": data_manual.year,
                        "Tecnico": tecnico,
                        "Setor": setor,
                        "Descricao": descricao
                    }])
                    
                    # Unimos o antigo com o novo (Append)
                    df_final = pd.concat([df_antigo, nova_linha], ignore_index=True)
                    
                    # Atualizamos a planilha com a lista completa
                    conn.update(worksheet="dados", data=df_final)
                    
                    st.success("Atividade gravada com sucesso!")
                except Exception:
                    st.error("Erro técnico ao salvar:")
                    st.code(traceback.format_exc())

elif aba == "Relatório Mensal":
    st.header("📊 Resumo de Produtividade")
    
    try:
        # Lê os dados mais recentes
        df = conn.read(worksheet="dados", ttl=0)
        
        if not df.empty:
            # Filtro de Mês
            meses_disponiveis = sorted(df['Mes'].unique(), reverse=True)
            mes_selecionado = st.selectbox("Selecione o Mês para o Relatório", meses_disponiveis)
            
            # Filtragem do DataFrame
            df_mes = df[df['Mes'] == mes_selecionado]
            
            # Indicadores Rápidos
            c1, c2 = st.columns(2)
            c1.metric("Total de Chamados no Mês", len(df_mes))
            c2.metric("Setor mais atendido", df_mes['Setor'].mode()[0] if not df_mes.empty else "-")
            
            # Gráficos
            st.subheader("Produção por Técnico")
            st.bar_chart(df_mes['Tecnico'].value_counts())
            
            st.subheader("Distribuição por Setor")
            st.bar_chart(df_mes['Setor'].value_counts())
            
            # Tabela detalhada
            with st.expander("Ver lista completa de atividades"):
                st.dataframe(df_mes, use_container_width=True)
        else:
            st.info("A planilha ainda não possui dados registrados.")
            
    except Exception:
        st.error("Não foi possível gerar o relatório. Verifique se a aba 'dados' existe e tem cabeçalhos.")
        st.code(traceback.format_exc())

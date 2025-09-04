import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from streamlit_autorefresh import st_autorefresh 
from io import BytesIO
import base64
from PIL import Image
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime

# Mapas de dias da semana em português
dias_semana = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']

hoje = datetime.now()
dia_semana = dias_semana[hoje.weekday()]  # weekday(): 0 = segunda ... 6 = domingo
data_formatada = f"{dia_semana} - {hoje.day:02d}/{hoje.month:02d}/{hoje.year}"



# ---- Tela cheia + tema escuro da PRECS ----
st.set_page_config(page_title="Precs Propostas", layout="wide")

# Estilo personalizado com identidade visual PRECS melhorada
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    header {
        visibility: hidden;
    }
    
    body {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0d0d0d 100%);
        color: white;
        margin: 0;
        padding: 0;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0d0d0d 100%);
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0d0d0d 100%);
        padding: 0;
        max-width: 100%;
    }
    
    h1, h2, h3, h4 {
        color: #FFD700;
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
        color: #000;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #e6c200 0%, #FFD700 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }
    
    .block-container {
        padding: 2rem;
        max-width: 100%;
    }
    
    .css-1v0mbdj {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%) !important;
        color: white;
        border-radius: 12px;
        border: 1px solid #333;
    }
    
    .css-1d391kg {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%) !important;
        border-radius: 12px;
        border: 1px solid #333;
    }
    
    .stDataFrame {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        color: white;
        border-radius: 12px;
        border: 1px solid #333;
    }
    
    /* Cards personalizados */
    .card {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%);
        border: 2px solid #C5A45A;
        border-radius: 0px;
        padding: 20px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border-color: #FFD700;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px #FFD700; }
        50% { box-shadow: 0 0 20px #FFD700, 0 0 30px #FFD700; }
        100% { box-shadow: 0 0 5px #FFD700; }
    }
    
    /* Animação de esteira vertical para nomes */
    @keyframes scrollVertical {
        0% { 
            transform: translateY(0); 
        }
        100% { 
            transform: translateY(-33.33%); 
        }
    }
    
    .scrolling-names {
        animation: scrollVertical 15s linear infinite;
        display: flex;
        flex-direction: column;
        width: 100%;
    }
    
    .name-row {
        min-height: 100px;
        display: flex;
        align-items: center;
        padding: 15px;
        margin: 0;
        border-bottom: 2px solid #C5A45A;
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%);
        transition: all 0.3s ease;
        flex-shrink: 0;
    }
    
    .name-row:hover {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 215, 0, 0.08) 100%);
        transform: scale(1.02);
    }
    
    .table-container {
        height: 70vh;
        overflow: hidden;
        position: relative;
        border: 2px solid #C5A45A;
        background: #000000;
        border-radius: 0px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .header-fixed {
        position: sticky;
        top: 0;
        z-index: 100;
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        border-bottom: 3px solid #FFD700;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    .animate-fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    .animate-pulse {
        animation: pulse 2s infinite;
    }
    
    .animate-glow {
        animation: glow 2s infinite;
    }
    
    /* Progress bars melhoradas */
    .progress-container {
        background: linear-gradient(135deg, #2C2C2C 0%, #1a1a1a 100%);
        border: 2px solid #D4AF37;
        border-radius: 0px;
        overflow: hidden;
        position: relative;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 0px;
        transition: width 0.8s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Tabela melhorada */
    .modern-table {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%);
        border-radius: 0px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 2px solid #C5A45A;
    }
    
    .modern-table th {
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        color: #FFD700;
        font-weight: 600;
        padding: 16px;
        font-size: 18px;
        text-align: center;
        border-bottom: 2px solid #FFD700;
    }
    
    .modern-table td {
        padding: 16px;
        font-size: 16px;
        border-bottom: 1px solid #333;
        transition: background-color 0.3s ease;
    }
    
    .modern-table tr:hover td {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
    }
    
    /* Medalha animada */
    .medal {
        animation: pulse 2s infinite;
        filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
    }
    
    /* Logo container */
    .logo-container {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%);
        border-radius: 0px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #C5A45A;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Campanhas ativas */
    .campanha-item {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
        border: 2px solid #C5A45A;
        border-radius: 0px;
        padding: 12px 20px;
        margin: 8px 0;
        text-align: center;
        font-size: 18px;
        font-weight: 500;
        color: #FFF;
        transition: all 0.3s ease;
    }
    
    .campanha-item:hover {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 215, 0, 0.1) 100%);
        transform: scale(1.02);
    }
    
    /* Cards pequenos */
    .small-card {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%);
        border: 2px solid #C5A45A;
        border-radius: 8px;
        padding: 12px;
        margin: 8px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        position: relative;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .small-card:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        border-color: #FFD700;
    }
    
    .small-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px solid #C5A45A;
    }
    
    .small-card-name {
        font-size: 16px;
        font-weight: 700;
        color: #FFFFFF;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
    }
    
    .small-card-metrics {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .small-metric {
        flex: 1;
        text-align: center;
    }
    
    .small-metric-label {
        font-size: 10px;
        color: #FFD700;
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .small-metric-value {
        font-size: 14px;
        color: #FFFFFF;
        font-weight: 700;
        margin: 2px 0;
    }
    
    .small-progress {
        width: 100%;
        height: 8px;
        background: linear-gradient(135deg, #2C2C2C 0%, #1a1a1a 100%);
        border: 1px solid #C5A45A;
        border-radius: 0px;
        overflow: hidden;
        margin: 4px 0;
    }
    
    .small-progress-bar {
        height: 100%;
        border-radius: 0px;
        transition: width 0.8s ease-in-out;
    }
    
    .cards-small-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        padding: 15px 0;
    }
    
    .traditional-table {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%);
        border-radius: 0px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 2px solid #C5A45A;
        width: 100%;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FFD700 0%, #e6c200 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #e6c200 0%, #FFD700 100%);
    }
    
    /* Responsividade */
    @media screen and (max-width: 1200px) {
        html, body, [class*="css"] {
            font-size: 11px !important;
        }
        
        h1, h2, h3, h4 {
            font-size: 14px !important;
        }
        
        .modern-table th,
        .modern-table td {
            font-size: 9px !important;
            padding: 4px !important;
        }
        
        .stButton>button {
            font-size: 9px !important;
            padding: 4px 8px !important;
        }
        
        .logo-container {
            padding: 8px;
        }
        
        .campanha-item {
            font-size: 10px;
            padding: 4px 6px;
        }
        
        .block-container {
            padding: 1rem !important;
        }
        
        .stColumns {
            gap: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ---- Autoatualização (a cada 10 segundos) ----
st_autorefresh(interval=60 * 1000, key="atualizacao")

print(f"Página atualizada em: {datetime.now().strftime('%H:%M:%S')}")

def image_to_base64(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    return img_b64

# ---- Carrega variáveis do .env ----
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ---- Conectar ao PostgreSQL ----
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )

# ---- Carregar dados ----
@st.cache_data(ttl=10)
def carregar_dados_propostas():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM dashmetas", conn)
    df["data"] = pd.to_datetime(df["data"])
    conn.close()
    return df

@st.cache_data(ttl=10)
def carregar_dados_campanhas():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM campanhas", conn)
    conn.close()
    return df

def atualizar_status_campanhas(campanhas_selecionadas):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE campanhas SET status_campanha = FALSE")
        for campanha in campanhas_selecionadas:
            cur.execute(
                "UPDATE campanhas SET status_campanha = TRUE WHERE nome_campanha = %s",
                (campanha,)
            )
        conn.commit()
    except Exception as e:
        st.error(f"Erro ao atualizar status das campanhas: {e}")
    finally:
        cur.close()
        conn.close()

def contar_propostas(df, df_original):
    # Garante que a coluna 'data' é datetime no df_original
    df_original['data'] = pd.to_datetime(df_original['data'])

    # PRIMEIRO: Remove duplicatas do dataset COMPLETO (antes de qualquer filtro)
    # Ordena pela data (da mais recente primeiro)
    df_original_sorted = df_original.sort_values(by='data', ascending=False)
    
    # Mantém a última vez que cada negócio passou por cada etapa (no dataset completo)
    df_original_ultimos = df_original_sorted.drop_duplicates(subset=['id_negocio', 'id_etapa'], keep='first')

    # SEGUNDO: Aplica os mesmos filtros que foram aplicados no df para manter consistência
    # Para isso, precisamos identificar quais registros estão no df filtrado
    # e aplicar os mesmos filtros no df_original_ultimos
    
    # Garante que a coluna 'data' é datetime no df filtrado também
    df['data'] = pd.to_datetime(df['data'])
    
    # Cria uma lista dos IDs únicos dos registros que passaram pelo filtro
    indices_filtrados = df.index.tolist()
    
    # Aplicar os mesmos filtros no df_original_ultimos
    # Primeiro, identifica as datas do período filtrado
    if not df.empty:
        data_min = df['data'].min()
        data_max = df['data'].max()
        proprietarios_filtrados = df['proprietario'].unique()
        etapas_filtradas = df['id_etapa'].unique()
        
        # Aplica filtros no df dedupliado
        df_ultimos = df_original_ultimos[
            (df_original_ultimos['data'] >= data_min) &
            (df_original_ultimos['data'] <= data_max) &
            (df_original_ultimos['proprietario'].isin(proprietarios_filtrados)) &
            (df_original_ultimos['id_etapa'].isin(etapas_filtradas))
        ]
    else:
        df_ultimos = df_original_ultimos.copy()

    # Lista de todos os proprietários do dataset filtrado
    all_proprietarios = df['proprietario'].unique() if not df.empty else df_original['proprietario'].unique()

    # Contagem de negócios que passaram pela etapa 'Cálculo' (última vez de cada um)
    df_adquiridas = df_ultimos[df_ultimos['id_etapa'] == 'Cálculo'] \
        .groupby('proprietario').agg(quantidade_adquiridas=('id_negocio', 'nunique')).reset_index()

    # Contagem de negócios que passaram pela etapa 'Negociações iniciadas' (última vez de cada um)
    df_apresentadas = df_ultimos[df_ultimos['id_etapa'] == 'Negociações iniciadas'] \
        .groupby('proprietario').agg(quantidade_apresentadas=('id_negocio', 'nunique')).reset_index()

    # Garante todos os proprietários no resultado final
    df_adquiridas_full = pd.DataFrame({'proprietario': all_proprietarios}) \
        .merge(df_adquiridas, on='proprietario', how='left').fillna(0)
    
    df_apresentadas_full = pd.DataFrame({'proprietario': all_proprietarios}) \
        .merge(df_apresentadas, on='proprietario', how='left').fillna(0)

    # Junta os resultados
    return pd.merge(df_adquiridas_full, df_apresentadas_full, on='proprietario', how='outer').fillna(0)

def get_cor_barra(valor, maximo=6):
    if valor >= maximo:
        return "background-color: #FFD700; box-shadow: 0 0 5px #FFD700, 0 0 10px #FFD700, 0 0 15px #FFD700;"
    return "background-color: #c3a43e;"



df_original = carregar_dados_propostas()
df = df_original.copy()
df_campanhas = carregar_dados_campanhas()

# ---- Sidebar ----
with st.sidebar:
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%); border-radius: 0px; padding: 12px; margin-bottom: 15px; border: 2px solid #C5A45A; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);">
            <h3 style="color: #FFFFFF; text-align: center; margin-bottom: 12px; font-weight: 600; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3); font-size: 14px;">🔧 Filtros</h3>
        </div>
    """, unsafe_allow_html=True)
    
    mostrar_gestao = st.checkbox("👥 Mostrar proprietário 'Gestão'", value=False)
    
    proprietarios_disponiveis = df["proprietario"].unique().tolist()
    if not mostrar_gestao:
        proprietarios_disponiveis = [p for p in proprietarios_disponiveis if p != "Gestão"]
    
    proprietarios = st.multiselect("👤 Proprietário", options=proprietarios_disponiveis, default=proprietarios_disponiveis)
    etapas = st.multiselect("📋 Etapa", df["id_etapa"].unique(), default=df["id_etapa"].unique())
    data_ini = st.date_input("📅 Data inicial", df["data"].max().date())
    data_fim = st.date_input("📅 Data final", df["data"].max().date())
    
    campanhas_disponiveis = df_campanhas["nome_campanha"].tolist()
    campanhas_selecionadas = st.multiselect(
        "🎯 Campanhas",
        options=campanhas_disponiveis,
        default=df_campanhas[df_campanhas["status_campanha"] == True]["nome_campanha"].tolist(),
        key="campanhas_filtro"
    )
    
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%); border-radius: 0px; padding: 12px; margin: 15px 0; border: 2px solid #C5A45A; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);">
            <h3 style="color: #FFFFFF; text-align: center; margin-bottom: 12px; font-weight: 600; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3); font-size: 14px;">🎨 Layout</h3>
        </div>
    """, unsafe_allow_html=True)
    
    layout_opcao = st.selectbox(
        "Escolha o layout:",
        ["Esteira Rolante", "Cards Pequenos", "Tabela Tradicional"],
        index=0
    )

atualizar_status_campanhas(campanhas_selecionadas)

if not mostrar_gestao:
    df = df[df["proprietario"] != "Gestão"]
    df_original = df_original[df_original["proprietario"] != "Gestão"]

df_filtrado = df.copy()
if proprietarios:
    df_filtrado = df_filtrado[df_filtrado["proprietario"].isin(proprietarios)]
if etapas:
    df_filtrado = df_filtrado[df_filtrado["id_etapa"].isin(etapas)]
df_filtrado = df_filtrado[
    (df_filtrado["data"].dt.date >= data_ini) &
    (df_filtrado["data"].dt.date <= data_fim)
]

df_propostas = contar_propostas(df_filtrado, df_original)
total_adquiridas = df_propostas['quantidade_adquiridas'].sum()
total_apresentadas = df_propostas['quantidade_apresentadas'].sum()

 

# ---- Visualizações principais ----
col2, col1 = st.columns([1,3])

with col1:
    medalha_b64 = image_to_base64("medalha.png")
    if not df_propostas.empty:
        maximo = 6
        
        if layout_opcao == "Esteira Rolante":
            # Código da esteira rolante
            linhas_dados = []
            for _, row in df_propostas.iterrows():
                nome = row['proprietario']
                valor1 = int(row['quantidade_adquiridas'])
                valor2 = int(row['quantidade_apresentadas'])
                medalha_html = f"""<img src="data:image/png;base64,{medalha_b64}" width="25" style="margin-left: 10px; vertical-align: middle;" class="medal">""" \
                    if valor1 >= 6 or valor2 >= 6 else ""
                
                proporcao1 = min(valor1 / maximo, 1.0)
                proporcao2 = min(valor2 / maximo, 1.0)
                cor_barra1 = get_cor_barra(valor1)
                cor_barra2 = get_cor_barra(valor2)

                barra1 = f"""
                <div class="progress-container" style='width: 100%; height: 15px; margin: 5px 0; border: 2px solid #C5A45A;'>
                    <div class="progress-bar" style='width: {proporcao1*100:.1f}%; {cor_barra1} height: 100%; border-radius: 0px;'></div>
                </div>
                <div style='font-size: 16px; color: #FFFFFF; font-weight: 700; text-align: center; margin-top: 5px;'>{valor1}/{maximo}</div>
                """

                barra2 = f"""
                <div class="progress-container" style='width: 100%; height: 15px; margin: 5px 0; border: 2px solid #C5A45A;'>
                    <div class="progress-bar" style='width: {proporcao2*100:.1f}%; {cor_barra2} height: 100%; border-radius: 0px;'></div>
                </div>
                <div style='font-size: 16px; color: #FFFFFF; font-weight: 700; text-align: center; margin-top: 5px;'>{valor2}/{maximo}</div>
                """

                linha = f"""
                <div class="name-row">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; width: 100%; align-items: center; height: 100%;">
                        <div style="display: flex; align-items: center; font-size: 26px; color: #FFFFFF; font-weight: 700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);">
                            {nome} {medalha_html}
                        </div>
                        <div style="text-align: center;">
                            {barra1}
                        </div>
                        <div style="text-align: center;">
                            {barra2}
                        </div>
                    </div>
                </div>
                """
                linhas_dados.append(linha)
            
            html_completo = f"""
            <style>
            body {{ margin: 0; padding: 0; }}
            @keyframes moveUp {{
                0% {{ transform: translateY(0px); }}
                100% {{ transform: translateY(-{len(linhas_dados) * 100}px); }}
            }}
            .main-container {{
                width: 100%;
                overflow: visible;
            }}
            .esteira-container {{
                height: 800px;
                overflow: hidden;
                border: 3px solid #C5A45A;
                background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0d0d0d 100%);
                position: relative;
            }}
            .esteira-content {{
                animation: moveUp {len(linhas_dados) * 5}s linear infinite;
            }}
            .linha-item {{
                height: 50px;
                display: flex;
                align-items: center;
                padding: 15px;
                border-bottom: 2px solid #C5A45A;
                background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%);
            }}
            </style>
            <div class="main-container">
                <div style="background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%); border: 3px solid #FFD700; padding: 15px; margin-bottom: 10px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; text-align: center;">
                        <div style="color: #FFD700; font-size: 20px; font-weight: 700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);">Nomes</div>
                        <div style="color: #FFD700; font-size: 20px; font-weight: 700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);">Adquiridas: {int(total_adquiridas)}/90</div>
                        <div style="color: #FFD700; font-size: 20px; font-weight: 700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);">Apresentadas: {int(total_apresentadas)}/90</div>
                    </div>
                </div>
                <div class="esteira-container">
                    <div class="esteira-content">
                        {"".join([linha.replace('class="name-row"', 'class="linha-item"') for linha in linhas_dados * 4])}
                    </div>
                </div>
            </div>
            """
            components.html(html_completo, height=900, scrolling=True)
            
        elif layout_opcao == "Cards Pequenos":
            # Cards pequenos
            cards_html = f"""
            <style>
            body {{ margin: 0; padding: 0; }}
            .main-container {{
                width: 100%;
                padding: 0;
                margin: 0;
                overflow: visible;
            }}
            .cards-small-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
                padding: 15px;
                max-width: 100%;
            }}
            .small-card {{
                background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%);
                border: 2px solid #C5A45A;
                border-radius: 8px;
                padding: 12px;
                margin: 8px;
                backdrop-filter: blur(10px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
                position: relative;
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .small-card:hover {{
                transform: translateY(-3px) scale(1.01);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
                border-color: #FFD700;
            }}
            .small-card-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
                padding-bottom: 8px;
                border-bottom: 1px solid #C5A45A;
            }}
            .small-card-name {{
                font-size: 16px;
                font-weight: 700;
                color: #FFFFFF;
                text-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
            }}
            .small-card-metrics {{
                display: flex;
                gap: 8px;
                align-items: center;
            }}
            .small-metric {{
                flex: 1;
                text-align: center;
            }}
            .small-metric-label {{
                font-size: 10px;
                color: #FFD700;
                font-weight: 600;
                margin-bottom: 4px;
            }}
            .small-metric-value {{
                font-size: 14px;
                color: #FFFFFF;
                font-weight: 700;
                margin: 2px 0;
            }}
            .small-progress {{
                width: 100%;
                height: 8px;
                background: linear-gradient(135deg, #2C2C2C 0%, #1a1a1a 100%);
                border: 1px solid #C5A45A;
                border-radius: 0px;
                overflow: hidden;
                margin: 4px 0;
            }}
            .small-progress-bar {{
                height: 100%;
                border-radius: 0px;
                transition: width 0.8s ease-in-out;
            }}
            </style>
            <div class="main-container">
                
                <div class="cards-small-grid">
            """
            
            for _, row in df_propostas.iterrows():
                nome = row['proprietario']
                valor1 = int(row['quantidade_adquiridas'])
                valor2 = int(row['quantidade_apresentadas'])
                
                tem_medalha = valor1 >= 6 or valor2 >= 6
                medalha_html = f"""<img src="data:image/png;base64,{medalha_b64}" width="16" style="margin-left: 5px;" class="medal">""" if tem_medalha else ""
                
                proporcao1 = min(valor1 / maximo, 1.0)
                proporcao2 = min(valor2 / maximo, 1.0)
                cor_barra1 = get_cor_barra(valor1).replace('background-color:', '').replace(';', '').split('box-shadow')[0].strip()
                cor_barra2 = get_cor_barra(valor2).replace('background-color:', '').replace(';', '').split('box-shadow')[0].strip()
                
                cards_html += f"""
                <div class="small-card">
                    <div class="small-card-header">
                        <div class="small-card-name">{nome} {medalha_html}</div>
                    </div>
                    <div class="small-card-metrics">
                        <div class="small-metric">
                            <div class="small-metric-label">ADQUIRIDAS</div>
                            <div class="small-progress">
                                <div class="small-progress-bar" style="width: {proporcao1*100:.1f}%; background-color: {cor_barra1};"></div>
                            </div>
                            <div class="small-metric-value">{valor1}/{maximo}</div>
                        </div>
                        <div class="small-metric">
                            <div class="small-metric-label">APRESENTADAS</div>
                            <div class="small-progress">
                                <div class="small-progress-bar" style="width: {proporcao2*100:.1f}%; background-color: {cor_barra2};"></div>
                            </div>
                            <div class="small-metric-value">{valor2}/{maximo}</div>
                        </div>
                    </div>
                </div>
                """
            
            cards_html += '</div></div>'
            # Calcular altura baseada no número de linhas no grid
            num_pessoas = len(df_propostas)
            linhas_grid = (num_pessoas + 3) // 4  # 4 cards por linha
            altura_cards = max(400, linhas_grid * 180 + 150)  # 180px por linha + margem maior
            components.html(cards_html, height=altura_cards, scrolling=True)
            
        else:  # Tabela Tradicional
            tabela_html = f"""
            <style>
            body {{ margin: 0; padding: 0; }}
            .main-container {{
                width: 100%;
                padding: 0;
                margin: 0;
                overflow: visible;
            }}
            .traditional-table {{
                background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(42, 42, 42, 0.95) 100%);
                border-radius: 0px;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); 
                width: 100%;
                max-width: 100%;
            }}
            .progress-container {{
                background: linear-gradient(135deg, #2C2C2C 0%, #1a1a1a 100%);
                border: 2px solid #D4AF37;
                border-radius: 0px;
                overflow: hidden;
                position: relative;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
            }}
            .progress-bar {{
                height: 100%;
                border-radius: 0px;
                transition: width 0.8s ease-in-out;
                position: relative;
                overflow: hidden;
            }}
            </style>
            <div class="main-container">
                <h2 style="text-align: center; color: #FFD700; font-size: 24px; font-weight: 700; text-shadow: 0 0 15px rgba(255, 215, 0, 0.8); margin-bottom: 20px;">
                    📊 Tabela Completa
                </h2>
                <div class="traditional-table">
                <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);">
                        <th style="color: #FFD700; font-size: 18px; font-weight: 700; padding: 15px; border: 1px solid #C5A45A;">Nome</th>
                        <th style="color: #FFD700; font-size: 18px; font-weight: 700; padding: 15px; border: 1px solid #C5A45A;">Adquiridas: {int(total_adquiridas)}/90</th>
                        <th style="color: #FFD700; font-size: 18px; font-weight: 700; padding: 15px; border: 1px solid #C5A45A;">Apresentadas: {int(total_apresentadas)}/90</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for _, row in df_propostas.iterrows():
                nome = row['proprietario']
                valor1 = int(row['quantidade_adquiridas'])
                valor2 = int(row['quantidade_apresentadas'])
                medalha_html = f"""<img src="data:image/png;base64,{medalha_b64}" width="20" style="margin-left: 10px; vertical-align: middle;" class="medal">""" \
                    if valor1 >= 6 or valor2 >= 6 else ""
                
                proporcao1 = min(valor1 / maximo, 1.0)
                proporcao2 = min(valor2 / maximo, 1.0)
                cor_barra1 = get_cor_barra(valor1)
                cor_barra2 = get_cor_barra(valor2)
                
                barra1 = f"""
                <div class="progress-container" style='width: 100%; height: 15px; margin: 5px 0; border: 1px solid #C5A45A;'>
                    <div class="progress-bar" style='width: {proporcao1*100:.1f}%; {cor_barra1} height: 100%; border-radius: 0px;'></div>
                </div>
                <span style='font-size: 16px; color: #FFFFFF; font-weight: 600;'>{valor1}/{maximo}</span>
                """
                
                barra2 = f"""
                <div class="progress-container" style='width: 100%; height: 15px; margin: 5px 0; border: 1px solid #C5A45A;'>
                    <div class="progress-bar" style='width: {proporcao2*100:.1f}%; {cor_barra2} height: 100%; border-radius: 0px;'></div>
                </div>
                <span style='font-size: 16px; color: #FFFFFF; font-weight: 600;'>{valor2}/{maximo}</span>
                """
                
                tabela_html += f"""
                <tr style="border-bottom: 1px solid #C5A45A; transition: all 0.3s ease;">
                    <td style="font-size: 20px; padding: 12px; color: #FFFFFF; vertical-align: middle; text-align: left; font-weight: 600; border: 1px solid #C5A45A;">
                        {nome} {medalha_html}
                    </td>
                    <td style="padding: 12px; color: #FFFFFF; vertical-align: middle; text-align: center; border: 1px solid #C5A45A;">
                        {barra1}
                    </td>
                    <td style="padding: 12px; color: #FFFFFF; vertical-align: middle; text-align: center; border: 1px solid #C5A45A;">
                        {barra2}
                    </td>
                </tr>
                """
            
            tabela_html += "</tbody></table></div></div>"
            # Calcular altura baseada no número de pessoas
            num_pessoas = len(df_propostas)
            altura_tabela = max(500, num_pessoas * 100 + 200)  # 100px por linha + cabeçalho maior
            components.html(tabela_html, height=altura_tabela, scrolling=True)


with col2:
    logo_b64 = image_to_base64("precs2.png")
    sino_b64 = image_to_base64("sino.png")  # Seu arquivo de sino
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; margin: 20px 0;"> 
            <img src="data:image/png;base64,{logo_b64}" width="500" style="border-radius: 10px;">
        </div> 
    """, unsafe_allow_html=True)
    
    # Cabeçalho com logo e título
    st.markdown(f"""
        <div class="animate-fade-in" style="display: flex; justify-content: center; align-items: center; text-align: center; margin: 10px 0;">
            <h1 style="font-size: 40px; color: #FFFFFF; margin: 0; font-weight: 700; text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);">Precs Propostas</h1> 
        </div>
        <h3 style='font-size: 18px; color: #FFFFFF; font-weight: 600; text-align: center; margin: 6px 0;'>
             {data_formatada}
         </h3>
    """, unsafe_allow_html=True) 

    # Título das campanhas + sino
    st.markdown("""
        <h2 style='text-align: center; color: #FFFFFF; margin: 15px 0 10px 0; font-weight: 600; text-shadow: 0 0 6px rgba(255, 255, 255, 0.3); font-size: 26px;'>🎯 Campanhas Ativas</h2>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <img src="data:image/png;base64,{sino_b64}" width="80px;" class="animate-pulse">
        </div>
    """, unsafe_allow_html=True)

    # Lista de campanhas
    campanhas_ativas = df_campanhas[df_campanhas["status_campanha"] == True]
    for _, campanha in campanhas_ativas.iterrows():
        st.markdown(f"""
            <div class="campanha-item animate-fade-in" style="display: flex; justify-content: center; align-items: center; text-align: center; margin-bottom: 8px;">
                <span style="font-size: 18px; color: #FFF; font-weight: 500;">🎯 {campanha['nome_campanha']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer com informações de atualização
    st.markdown(f"""
        <div class="animate-fade-in" style="margin-top: 20px; padding: 12px; background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(42, 42, 42, 0.9) 100%); border-radius: 0px; border: 2px solid #C5A45A; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3); text-align: center;">
            <div style="font-size: 10px; color: #FFFFFF; font-weight: 500;">
                🔄 Atualizado automaticamente a cada 60 segundos
            </div>
            <div style="font-size: 9px; color: #FFFFFF; margin-top: 3px;">
                Última atualização: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
    """, unsafe_allow_html=True)

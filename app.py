import streamlit as st
from fpdf import FPDF
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image

# --- CONFIGURAÇÕES DE ARQUIVO ---
DATA_FILE = "config_espelhos_vfinal.json"
LOGO_FILE = "logo_empresa.png"

def carregar_dados():
    # Valores Iniciais Completos (Baseado na sua planilha Vitrarte)
    padrao = {
        "fixos": {"valor_hora": 80.0, "energia_h": 0.70, "quebra_percent": 5.0, "imposto": 11.0},
        "insumos_m2": {
            "Chapa Espelho 3mm": 80.0, "MDF": 16.0, "Couro (m2)": 5.0, 
            "Adesivo Jateado": 8.5, "Hero Pack": 1.15
        },
        "insumos_linear": {
            "Fita de LED": 2.5, "E.V.A": 0.8, "Polietileno": 0.48, "Couro (Linear)": 2.65
        },
        "insumos_unit": {
            "Touch + Adesivo": 21.5, "Fonte": 18.0, "Pendurador": 1.5, "Caixa Papelão": 18.0, 
            "Cantoneira": 0.29, "Insumos Diversos": 40.0, "Caixa de Bateria": 3.2, 
            "Etiqueta Frágil": 0.16, "Bolha": 0.65, "Fita Frágil": 0.3, "Canaleta EPS": 4.4
        },
        "empresa": {"nome": "Vitrarte Espelhos", "end": "Seu Endereço", "fone": "Seu Fone", "email": "Seu Email"},
        "marketplace": {"ml_classico_taxa": 10.5, "ml_premium_taxa": 15.5, "ml_frete_perc": 12.0, "shopee_taxa_base": 14.0, "shopee_taxa_campanha": 6.0},
        "vendas": [], "produtos_cadastrados": {}
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Garante que chaves novas não quebrem o app
                for chave in padrao:
                    if chave not in data: data[chave] = padrao[chave]
                return data
        except: return padrao
    return padrao

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f)

# Inicialização
if 'dados' not in st.session_state: st.session_state.dados = carregar_dados()
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- CONFIGURAÇÃO DE PERFIS ---
PERFIS = {
    "Personalizado": {"m2": [], "linear": [], "unit": []},
    "Jateados": {"m2": ["Hero Pack", "Chapa Espelho 3mm", "Adesivo Jateado"], "linear": ["E.V.A", "Polietileno", "Fita de LED"], "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Touch + Adesivo", "Insumos Diversos"]},
    "Dupla Face": {"m2": ["Hero Pack", "Chapa Espelho 3mm"], "linear": ["Polietileno"], "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]},
    "Lapidado com LED": {"m2": ["Hero Pack", "Chapa Espelho 3mm"], "linear": ["Polietileno", "E.V.A", "Fita de LED"], "unit": ["Touch + Adesivo", "Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]},
    "Adnet": {"m2": ["Hero Pack", "Chapa Espelho 3mm"], "linear": ["Polietileno", "Couro (Linear)"], "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]},
    "Orgânicos": {"m2": ["Hero Pack", "Chapa Espelho 3mm", "Couro (m2)"], "linear": ["E.V.A", "Fita de LED", "Polietileno"], "unit": ["Touch + Adesivo", "Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]}
}

st.set_page_config(page_title="EspelhoMaster Pro", layout="wide")

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acesso - EspelhoMaster")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "VilaLaser2026":
            st.session_state.autenticado = True; st.rerun()
        else: st.error("Senha incorreta!")
    st.stop()

# --- FUNÇÃO PDF ---
def gerar_pdf(dados_v, itens):
    pdf = FPDF()
    pdf.add_page()
    try:
        if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, 10, 8, 30)
    except: pass
    pdf.set_font("Arial", 'B', 14); pdf.cell(80); pdf.cell(0, 10, st.session_state.dados['empresa']['nome'], ln=True)
    pdf.set_font("Arial", size=9); pdf.cell(80); pdf.cell(0, 5, f"Fone: {st.session_state.dados['empresa']['fone']}", ln=True)
    pdf.ln(15); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 7, f"ORÇAMENTO: {dados_v['cliente']}", ln=True)
    pdf.set_fill_color(240, 240, 240); pdf.cell(100, 8, " Item", 1, 0, 'L', True); pdf.cell(40, 8, " Qtd", 1, 0, 'C', True); pdf.cell(50, 8, " Total", 1, 1, 'C', True)
    for p in itens:
        pdf.cell(100, 8, f" {p['nome']}", 1); pdf.cell(40, 8, f" {p['qtd']}", 1, 0, 'C'); pdf.cell(50, 8, f" R$ {p['total_item']:.2f}", 1, 1, 'C')
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"TOTAL: R$ {dados_v['total']:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- INTERFACE ---
tabs = st.tabs(["📋 Orçamento", "📈 Marketplace", "💰 Caixa", "📦 Insumos", "🏷️ Catálogo", "🏢 Empresa", "📊 Resultado"])

# --- TAB 1: ORÇAMENTO ---
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("👤 Cliente")
        cli_n = st.text_input("Nome"); cli_f = st.text_input("WhatsApp"); cli_e = st.text_area("Endereço")
    with c2:
        st.subheader("🛠️ Cálculo")
        perfil = st.selectbox("Perfil:", list(PERFIS.keys()))
        col_d1, col_d2 = st.columns(2)
        alt = col_d1.number_input("Altura (m)", value=0.7); larg = col_d2.number_input("Largura (m)", value=0.7)
        area = alt * larg; perim = (alt + larg) * 2
        
        sel_m2 = st.multiselect("Insumos m²", list(st.session_state.dados["insumos_m2"].keys()), default=PERFIS[perfil]["m2"])
        sel_lin = st.multiselect("Lineares", list(st.session_state.dados["insumos_linear"].keys()), default=PERFIS[perfil]["linear"])
        sel_uni = st.multiselect("Unitários", list(st.session_state.dados["insumos_unit"].keys()), default=PERFIS[perfil]["unit"])
        markup = st.slider("Margem %", 0, 500, 100)
        
        c_tot = (sum(st.session_state.dados["insumos_m2"][m]*area for m in sel_m2) + 
                 sum(st.session_state.dados["insumos_linear"][l]*perim for l in sel_lin) + 
                 sum(st.session_state.dados["insumos_unit"][u] for u in sel_uni)) * 1.05
        venda = c_tot * (1 + markup/100)
        st.metric("Venda Sugerida", f"R$ {venda:.2f}", f"Custo: R$ {c_tot:.2f}")
        
        if st.button("🛒 Adicionar"):
            st.session_state.carrinho.append({"nome": f"Espelho {alt}x{larg}", "qtd": 1, "custo_t": c_tot, "total_item": venda})
            st.rerun()

    if st.session_state.carrinho:
        st.table(pd.DataFrame(st.session_state.carrinho)[['nome', 'qtd', 'total_item']])
        if st.button("✅ Salvar e Gerar PDF"):
            total_v = sum(p['total_item'] for p in st.session_state.carrinho)
            v_db = {"cliente": cli_n, "total": total_v, "custo": sum(p['custo_t'] for p in st.session_state.carrinho), "status": "Pendente", "data": datetime.now().strftime("%d/%m/%Y"), "itens": list(st.session_state.carrinho)}
            st.session_state.dados["vendas"].append(v_db); salvar_dados(st.session_state.dados)
            pdf = gerar_pdf({"cliente": cli_n, "fone": cli_f, "endereco": cli_e, "total": total_v}, st.session_state.carrinho)
            st.download_button("📥 Baixar PDF", pdf, f"Orcamento_{cli_n}.pdf")

# --- TAB 2: MARKETPLACE ---
with tabs[1]:
    st.header("📈 Marketplace")
    liq = st.number_input("Quanto deseja receber limpo?", value=250.0)
    m = st.session_state.dados["marketplace"]
    p_ml = liq / (1 - (m["ml_classico_taxa"] + m["ml_frete_perc"])/100)
    p_sh = (liq + 3) / (1 - (m["shopee_taxa_base"] + m["shopee_taxa_campanha"])/100)
    st.info(f"Venda ML: **R$ {p_ml:.2f}** | Venda Shopee: **R$ {p_sh:.2f}**")

# --- TAB 4: INSUMOS (RESTAURADOS) ---
with tabs[3]:
    st.header("📦 Preços Vitrarte")
    c_i1, c_i2, c_i3 = st.columns(3)
    with c_i1:
        for k, v in st.session_state.dados["insumos_m2"].items():
            st.session_state.dados["insumos_m2"][k] = st.number_input(k, value=float(v), key=f"m2_{k}")
    with c_i2:
        for k, v in st.session_state.dados["insumos_linear"].items():
            st.session_state.dados["insumos_linear"][k] = st.number_input(k, value=float(v), key=f"ln_{k}")
    with c_i3:
        for k, v in st.session_state.dados["insumos_unit"].items():
            st.session_state.dados["insumos_unit"][k] = st.number_input(k, value=float(v), key=f"un_{k}")
    if st.button("💾 Salvar Preços"): salvar_dados(st.session_state.dados); st.success("Salvo!")

# --- TAB 6: EMPRESA ---
with tabs[5]:
    st.header("🏢 Dados")
    st.session_state.dados["empresa"]["nome"] = st.text_input("Nome", st.session_state.dados["empresa"]["nome"])
    img_up = st.file_uploader("Logo PNG")
    if img_up:
        with open(LOGO_FILE, "wb") as f: f.write(img_up.getbuffer())
        st.image(LOGO_FILE, width=100)
    if st.button("Salvar Empresa"): salvar_dados(st.session_state.dados); st.success("Salvo!")

# (As abas de Caixa, Catálogo e Resultado seguem a mesma lógica funcional...)

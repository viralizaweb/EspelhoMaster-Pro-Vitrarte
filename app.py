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
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Verificações de segurança para não sumir nada
            if "marketplace" not in data: data["marketplace"] = {"ml_classico_taxa": 10.5, "ml_premium_taxa": 15.5, "ml_frete_perc": 12.0, "shopee_taxa_base": 14.0, "shopee_taxa_campanha": 6.0}
            if "empresa" not in data: data["empresa"] = {"nome": "Vitrarte Espelhos", "end": "", "fone": "", "email": ""}
            if "produtos_cadastrados" not in data: data["produtos_cadastrados"] = {}
            if "vendas" not in data: data["vendas"] = []
            return data
    
    # RESTAURAÇÃO DE TODOS OS INSUMOS DA PLANILHA
    return {
        "fixos": {"valor_hora": 80.0, "energia_h": 0.70, "quebra_percent": 5.0, "imposto": 11.0},
        "insumos_m2": {
            "Chapa Espelho 3mm": 80.0, "MDF Fundo": 16.0, "Couro (m2)": 5.0, 
            "Adesivo Jateado": 8.5, "Hero Pack": 1.15
        },
        "insumos_linear": {
            "Fita de LED": 2.5, "E.V.A (Linear)": 0.8, "Polietileno": 0.48, "Couro (Linear)": 2.65
        },
        "insumos_unit": {
            "Touch + Adesivo": 21.5, "Fonte": 18.0, "Pendurador": 1.5, "Caixa Papelão": 18.0, 
            "Cantoneira": 0.29, "Insumos Diversos": 40.0, "Caixa de Bateria": 3.2, 
            "Etiqueta Frágil": 0.16, "Bolha": 0.65, "Fita Frágil": 0.3
        },
        "empresa": {"nome": "Vitrarte Espelhos", "end": "", "fone": "", "email": ""},
        "marketplace": {"ml_classico_taxa": 10.5, "ml_premium_taxa": 15.5, "ml_frete_perc": 12.0, "shopee_taxa_base": 14.0, "shopee_taxa_campanha": 6.0},
        "vendas": [], "produtos_cadastrados": {}
    }

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f)

# Inicialização
if 'dados' not in st.session_state: st.session_state.dados = carregar_dados()
if 'carrinho' not in st.session_state: st.session_state.carrinho = []
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- CONFIGURAÇÃO DE PERFIS (TEMPLATES) ---
PERFIS = {
    "Personalizado": {"m2": [], "linear": [], "unit": []},
    "Jateados": {
        "m2": ["Hero Pack", "Chapa Espelho 3mm", "Adesivo Jateado"],
        "linear": ["E.V.A (Linear)", "Polietileno", "Fita de LED"],
        "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Touch + Adesivo", "Insumos Diversos"]
    },
    "Dupla Face": {
        "m2": ["Hero Pack", "Chapa Espelho 3mm"],
        "linear": ["Polietileno"],
        "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]
    },
    "Lapidado com LED": {
        "m2": ["Hero Pack", "Chapa Espelho 3mm"],
        "linear": ["Polietileno", "E.V.A (Linear)", "Fita de LED"],
        "unit": ["Touch + Adesivo", "Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]
    },
    "Adnet": {
        "m2": ["Hero Pack", "Chapa Espelho 3mm"],
        "linear": ["Polietileno", "Couro (Linear)"],
        "unit": ["Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]
    },
    "Orgânicos": {
        "m2": ["Hero Pack", "Chapa Espelho 3mm", "Couro (m2)"],
        "linear": ["E.V.A (Linear)", "Fita de LED", "Polietileno"],
        "unit": ["Touch + Adesivo", "Cantoneira", "Caixa Papelão", "Pendurador", "Insumos Diversos"]
    }
}

st.set_page_config(page_title="EspelhoMaster Pro", layout="wide")

# --- LOGIN ---
if not st.session_state.autenticado:
    st.title("🔐 Acesso - EspelhoMaster Pro")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == "VilaLaser2026":
            st.session_state.autenticado = True; st.rerun()
        else: st.error("Senha incorreta!")
    st.stop()

# --- HEADER ---
col_logo, col_tit = st.columns([1, 4])
if os.path.exists(LOGO_FILE): col_logo.image(LOGO_FILE, width=120)
col_tit.title(f"💎 {st.session_state.dados['empresa']['nome']}")

# --- FUNÇÃO PDF ---
def gerar_pdf(dados_v, itens):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(LOGO_FILE): pdf.image(LOGO_FILE, 10, 8, 30)
    pdf.set_font("Arial", 'B', 14); pdf.cell(80); pdf.cell(0, 10, st.session_state.dados['empresa']['nome'], ln=True)
    pdf.set_font("Arial", size=9); pdf.cell(80); pdf.cell(0, 5, f"Fone: {st.session_state.dados['empresa']['fone']} | {st.session_state.dados['empresa']['email']}", ln=True)
    pdf.ln(15); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 7, f"ORÇAMENTO: {dados_v['cliente']}", ln=True)
    pdf.set_font("Arial", size=10); pdf.cell(0, 6, f"Endereço: {dados_v['endereco']}", ln=True); pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.cell(100, 8, " Item", 1, 0, 'L', True); pdf.cell(40, 8, " Qtd", 1, 0, 'C', True); pdf.cell(50, 8, " Total", 1, 1, 'C', True)
    for p in itens:
        pdf.cell(100, 8, f" {p['nome']}", 1); pdf.cell(40, 8, f" {p['qtd']}", 1, 0, 'C'); pdf.cell(50, 8, f" R$ {p['total_item']:.2f}", 1, 1, 'C')
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, f"TOTAL: R$ {dados_v['total']:.2f}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- ABAS ---
tabs = st.tabs(["📋 Orçamento", "📈 Marketplace", "💰 Caixa", "📦 Insumos", "🏷️ Catálogo", "🏢 Empresa", "📊 Dashboard"])

# --- TAB 1: ORÇAMENTO ---
with tabs[0]:
    c1, c2 = st.columns([1, 1.5])
    with c1:
        st.subheader("👤 Cliente")
        cli_n = st.text_input("Nome"); cli_f = st.text_input("WhatsApp"); cli_e = st.text_area("Endereço do Cliente")
    with c2:
        st.subheader("🛠️ Cálculo do Espelho")
        perfil_sel = st.selectbox("Escolha um Perfil:", list(PERFIS.keys()))
        col_d1, col_d2 = st.columns(2)
        alt = col_d1.number_input("Altura (m)", value=0.7); larg = col_d2.number_input("Largura (m)", value=0.7)
        area = alt * larg; perim = (alt + larg) * 2
        
        sel_m2 = st.multiselect("Insumos m²", list(st.session_state.dados["insumos_m2"].keys()), default=PERFIS[perfil_sel]["m2"])
        sel_lin = st.multiselect("Lineares", list(st.session_state.dados["insumos_linear"].keys()), default=PERFIS[perfil_sel]["linear"])
        sel_uni = st.multiselect("Unitários", list(st.session_state.dados["insumos_unit"].keys()), default=PERFIS[perfil_sel]["unit"])
        markup = st.slider("Margem %", 0, 500, 100)
        
        custo = (sum(st.session_state.dados["insumos_m2"][m]*area for m in sel_m2) + sum(st.session_state.dados["insumos_linear"][l]*perim for l in sel_lin) + sum(st.session_state.dados["insumos_unit"][u] for u in sel_uni)) * 1.05
        venda = custo * (1 + markup/100)
        st.metric("Venda Unitária Sugerida", f"R$ {venda:.2f}", f"Custo: R$ {custo:.2f}")
        if st.button("🛒 Adicionar ao Orçamento"):
            st.session_state.carrinho.append({"nome": f"Espelho {alt}x{larg}", "qtd": 1, "custo_t": custo, "total_item": venda})
            st.rerun()

    if st.session_state.carrinho:
        st.table(pd.DataFrame(st.session_state.carrinho)[['nome', 'qtd', 'total_item']])
        tot_orc = sum(p['total_item'] for p in st.session_state.carrinho)
        cb1, cb2, cb3 = st.columns(3)
        if cb1.button("🗑️ Limpar"): st.session_state.carrinho = []; st.rerun()
        if cb2.button("✅ Salvar Venda"):
            v_db = {"cliente": cli_n, "total": tot_orc, "custo": sum(p['custo_t'] for p in st.session_state.carrinho), "status": "Pendente", "data": datetime.now().strftime("%d/%m/%Y"), "itens": list(st.session_state.carrinho)}
            st.session_state.dados["vendas"].append(v_db); salvar_dados(st.session_state.dados); st.session_state.carrinho = []; st.success("Venda Salva!")
        if cb3.button("🚀 Gerar PDF"):
            pdf = gerar_pdf({"cliente": cli_n, "fone": cli_f, "endereco": cli_e, "total": tot_orc}, st.session_state.carrinho)
            st.download_button("📥 Baixar PDF", pdf, f"Orcamento_{cli_n}.pdf")

# --- TAB 2: MARKETPLACE ---
with tabs[1]:
    st.header("📈 Simulador Mercado Livre & Shopee")
    liq = st.number_input("Valor Líquido que deseja receber (R$)", value=250.0)
    m = st.session_state.dados["marketplace"]
    p_ml_c = liq / (1 - (m["ml_classico_taxa"] + m["ml_frete_perc"])/100)
    p_ml_p = liq / (1 - (m["ml_premium_taxa"] + m["ml_frete_perc"])/100)
    p_sh_c = (liq + 3) / (1 - (m["shopee_taxa_base"] + m["shopee_taxa_campanha"])/100)
    st.info(f"Venda ML Clássico: **R$ {p_ml_c:.2f}** | ML Premium: **R$ {p_ml_p:.2f}** | Shopee Campanha: **R$ {p_sh_c:.2f}**")

# --- TAB 3: CAIXA ---
with tabs[2]:
    st.header("💰 Controle de Caixa")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.subheader("🔴 Pendentes")
        for i, v in enumerate(st.session_state.dados["vendas"]):
            if v["status"] == "Pendente":
                with st.expander(f"{v['cliente']} - R$ {v['total']:.2f}"):
                    if st.button("Marcar como Pago", key=f"pay_{i}"):
                        st.session_state.dados["vendas"][i]["status"] = "Pago"; salvar_dados(st.session_state.dados); st.rerun()
    with c_p2:
        st.subheader("🟢 Pagos")
        for i, v in enumerate(st.session_state.dados["vendas"]):
            if v["status"] == "Pago":
                with st.expander(f"{v['cliente']} - R$ {v['total']:.2f}"):
                    if st.button("Estornar", key=f"rev_{i}"):
                        st.session_state.dados["vendas"][i]["status"] = "Pendente"; salvar_dados(st.session_state.dados); st.rerun()

# --- TAB 4: INSUMOS (TODOS RECUPERADOS) ---
with tabs[3]:
    st.header("📦 Tabela de Preços de Insumos")
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        st.write("**Insumos por m²**")
        for k, v in st.session_state.dados["insumos_m2"].items():
            st.session_state.dados["insumos_m2"][k] = st.number_input(k, value=float(v), key=f"m2_{k}")
    with col_i2:
        st.write("**Insumos Lineares**")
        for k, v in st.session_state.dados["insumos_linear"].items():
            st.session_state.dados["insumos_linear"][k] = st.number_input(k, value=float(v), key=f"ln_{k}")
    with col_i3:
        st.write("**Insumos Unitários**")
        for k, v in st.session_state.dados["insumos_unit"].items():
            st.session_state.dados["insumos_unit"][k] = st.number_input(k, value=float(v), key=f"un_{k}")
    if st.button("💾 Salvar Tabela de Preços"): salvar_dados(st.session_state.dados); st.success("Preços Atualizados!")

# --- TAB 5: CATÁLOGO ---
with tabs[4]:
    st.header("🏷️ Catálogo de Produtos")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        n_p = st.text_input("Nome do Produto"); v_p = st.number_input("Custo Base")
        if st.button("Adicionar"):
            st.session_state.dados["produtos_cadastrados"][n_p] = v_p; salvar_dados(st.session_state.dados); st.rerun()
    with col_c2:
        for p, v in st.session_state.dados["produtos_cadastrados"].items():
            st.write(f"• {p}: R$ {v:.2f}")

# --- TAB 6: EMPRESA ---
with tabs[5]:
    st.header("🏢 Dados da Empresa")
    st.session_state.dados["empresa"]["nome"] = st.text_input("Nome da Empresa", st.session_state.dados["empresa"]["nome"])
    st.session_state.dados["empresa"]["fone"] = st.text_input("Fone/WhatsApp", st.session_state.dados["empresa"]["fone"])
    st.session_state.dados["empresa"]["email"] = st.text_input("E-mail", st.session_state.dados["empresa"]["email"])
    st.session_state.dados["empresa"]["end"] = st.text_area("Endereço", st.session_state.dados["empresa"]["end"])
    img_up = st.file_uploader("Upload da Logo (PNG/JPG)")
    if img_up:
        with open(LOGO_FILE, "wb") as f: f.write(img_up.getbuffer())
        st.image(LOGO_FILE, width=150)
    if st.button("Salvar Configurações"): salvar_dados(st.session_state.dados); st.success("Dados Salvos!")

# --- TAB 7: DASHBOARD ---
with tabs[6]:
    st.header("📊 Resultado Financeiro")
    if st.session_state.dados["vendas"]:
        df = pd.DataFrame(st.session_state.dados["vendas"])
        df['lucro'] = df['total'] - df['custo']
        st.metric("Lucro Acumulado", f"R$ {df['lucro'].sum():.2f}")
        st.bar_chart(df[['total', 'lucro']])
    else: st.info("Sem dados para exibir.")
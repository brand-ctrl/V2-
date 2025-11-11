
import streamlit as st
from modules.remover_fundo import render_removedor
from modules.extrair_imagens_csv import render_extrator
from modules.conversor import render_conversor
from modules.renderizar_videos import render_renderizador

st.set_page_config(page_title="V2 Tools", page_icon="⚙️", layout="centered")

st.title("🧰 V2 Ferramentas")

st.markdown("### Escolha uma ferramenta para iniciar:")

# Conversor
st.markdown('<div class="v2-card fade-in"><div class="v2-icon">🖼️</div><div class="v2-text"><p class="v2-title">CONVERSOR DE IMAGENS</p><p class="v2-desc">Redimensione para 1080×1080 ou 1080×1920 preenchendo com cor.</p></div></div>', unsafe_allow_html=True)
if st.button("Abrir Conversor", key="conv"):
    render_conversor()

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# Extrator
st.markdown('<div class="v2-card fade-in"><div class="v2-icon">📥</div><div class="v2-text"><p class="v2-title">EXTRATOR DE IMAGENS CSV</p><p class="v2-desc">Baixe imagens diretamente de URLs listadas em um arquivo CSV.</p></div></div>', unsafe_allow_html=True)
if st.button("Abrir Extrator CSV", key="ext"):
    render_extrator()

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# Removedor
st.markdown('<div class="v2-card fade-in"><div class="v2-icon">🧼</div><div class="v2-text"><p class="v2-title">REMOVEDOR DE FUNDO</p><p class="v2-desc">Remova fundos em lote com preview antes/depois e PNG de alta qualidade.</p></div></div>', unsafe_allow_html=True)
if st.button("Abrir Removedor de Fundo", key="rm"):
    render_removedor()

st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

# Novo: Renderizador de Vídeos
st.markdown('<div class="v2-card fade-in"><div class="v2-icon">🎬</div><div class="v2-text"><p class="v2-title">RENDERIZADOR DE VÍDEOS</p><p class="v2-desc">Sobreponha vídeos nos segundos finais. Suporte a múltiplos vídeos base por ZIP.</p></div></div>', unsafe_allow_html=True)
if st.button("Abrir Renderizador", key="render"):
    render_renderizador()

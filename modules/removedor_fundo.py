import streamlit as st
from PIL import Image
import io, os, shutil, zipfile, base64
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from rembg import remove, new_session
    _HAS_REMBG = True
except Exception:
    _HAS_REMBG = False


def _play_ping(ping_b64: str):
    st.markdown(f'<audio autoplay src="data:audio/wav;base64,{ping_b64}"></audio>', unsafe_allow_html=True)


def render(ping_b64: str):
    # ====== CARREGAR IMAGEM COMO BASE64 ======
    banner_path = "assets/removedor_banner.png"
    try:
        with open(banner_path, "rb") as f:
            b64_banner = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        st.error("❌ Imagem de banner não encontrada em 'assets/removedor_banner.png'")
        st.stop()

    # ====== CSS GLOBAL ======
    st.markdown("""
    <style>
    body,[class*="css"] {
        background-color: #f9fafb !important;
        color: #111 !important;
        font-family: 'Inter', sans-serif;
    }
    .stApp header, .stApp [data-testid="stHeader"], .block-container {
        background: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* HERO SECTION */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        margin-left: 10%;
        margin-top: 20px;
    }
    .hero-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 32px;
        color: #111;
    }
    .hero {
        position: relative;
        width: 500px;
        height: 500px;
        border-radius: 20px;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .hero img.bg {
        width: 500px;
        height: 500px;
        object-fit: cover;
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }

    /* EXPANDER E UPLOAD */
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] button {
        color: #111 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
    }

    /* ALERT HARMONIZADO */
    .custom-alert {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 18px;
        color: #111;
        font-size: 15px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ====== HERO SECTION ======
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">REMOVEDOR DE FUNDO</div>
        <div class="hero">
            <img src="data:image/png;base64,{b64_banner}" class="bg" alt="background">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ====== VERIFICAÇÃO DE BIBLIOTECA ======
    if not _HAS_REMBG:
        st.error("Biblioteca 'rembg' não encontrada. Instale com: pip install rembg onnxruntime")
        st.stop()

    # ====== CONFIGURAÇÕES ======
    with st.expander("⚙️ Configurações avançadas", expanded=False):
        model = st.selectbox(
            "Modelo",
            ("u2net_human_seg", "u2net", "isnet-general-use"),
            index=0,
            help="Escolha o modelo de recorte — o padrão é otimizado para pessoas."
        )
        st.caption("💡 Dica: 'u2net_human_seg' é ideal para retratos humanos.")

    # ====== UPLOAD ======
    files = st.file_uploader(
        "📂 Envie imagens ou um arquivo ZIP",
        type=["jpg", "jpeg", "png", "webp", "zip"],
        accept_multiple_files=True
    )
    if not files:
        st.markdown('<div class="custom-alert">👆 Envie suas imagens acima para começar.</div>', unsafe_allow_html=True)
        st.stop()

    INP, OUT = "rm_in", "rm_out"
    shutil.rmtree(INP, ignore_errors=True)
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(INP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    # ====== EXTRAÇÃO COMPLETA (ZIP COM SUBPASTAS) ======
    from zipfile import ZipFile, BadZipFile

    def extract_all(zip_file, extract_to):
        """Extrai ZIP incluindo subpastas preservando estrutura"""
        for member in zip_file.infolist():
            try:
                zip_file.extract(member, extract_to)
            except Exception as e:
                st.warning(f"Não foi possível extrair {member.filename}: {e}")

    for f in files:
        if f.name.lower().endswith(".zip"):
            try:
                with ZipFile(io.BytesIO(f.read())) as z:
                    extract_all(z, INP)
            except BadZipFile:
                st.error(f"❌ ZIP inválido: {f.name}")
        else:
            file_path = os.path.join(INP, f.name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as out:
                out.write(f.read())

    paths = [p for p in Path(INP).rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    if not paths:
        st.warning("Nenhuma imagem válida foi encontrada dentro das pastas enviadas.")
        st.stop()

    session = new_session(model)

    prog = st.progress(0.0)
    info = st.empty()
    previews = []

    def worker(p: Path):
        rel = p.relative_to(INP)
        raw = open(p, "rb").read()
        out_bytes = remove(raw, session=session)
        outp = (Path(OUT) / rel).with_suffix(".png")
        os.makedirs(outp.parent, exist_ok=True)
        open(outp, "wb").write(out_bytes)
        return raw, out_bytes, rel.as_posix()

    with ThreadPoolExecutor(max_workers=4) as ex:
        fut = [ex.submit(worker, p) for p in paths]
        tot = len(fut)
        for i, f in enumerate(as_completed(fut), 1):
            try:
                previews.append(f.result())
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
            prog.progress(i / tot)
            info.info(f"Processado {i}/{tot}")

    st.markdown("<hr style='border: 0; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)
    st.subheader("🖼️ Pré-visualização (Antes / Depois)")
    alpha = st.slider("Comparação de mistura", 0, 100, 50, 1)
    blend = alpha / 100.0

    cols = st.columns(2)
    for orig_b, out_b, name in previews[:3]:
        with cols[0]:
            st.image(orig_b, caption=f"ANTES — {name}", use_column_width=True)
        with cols[1]:
            try:
                img_o = Image.open(io.BytesIO(orig_b)).convert("RGBA")
                img_r = Image.open(io.BytesIO(out_b)).convert("RGBA")
                w = min(img_o.width, img_r.width)
                h = min(img_o.height, img_r.height)
                img_o = img_o.resize((w, h))
                img_r = img_r.resize((w, h))
                blended = Image.blend(img_o, img_r, blend)
                bio = io.BytesIO()
                blended.save(bio, format="PNG")
                bio.seek(0)
                st.image(bio, caption=f"DEPOIS — {name}", use_column_width=True)
            except Exception:
                st.image(out_b, caption=f"DEPOIS — {name}", use_column_width=True)

    # ====== CRIAR ZIP FINAL ======
    zbytes = io.BytesIO()
    with zipfile.ZipFile(zbytes, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for fn in files:
                fp = os.path.join(root, fn)
                arc = os.path.relpath(fp, OUT)
                z.write(fp, arc)
    zbytes.seek(0)

    st.success("✅ Remoção de fundo concluída!")
    _play_ping(ping_b64)
    st.download_button(
        "📦 Baixar PNGs sem fundo",
        data=zbytes,
        file_name="sem_fundo.zip",
        mime="application/zip",
        use_container_width=True
    )

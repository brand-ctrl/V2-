# 📦 Renderizador de Vídeos com Sobreposição (modo único ou em lote)

import os
import shutil
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from google.colab import files
from zipfile import ZipFile

# Criar pastas de trabalho
os.makedirs("inputs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def limpar_pastas():
    shutil.rmtree("inputs")
    shutil.rmtree("outputs")
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

limpar_pastas()

# 🎩 Perguntar o modo de execução
modo = input("Escolha o modo:\n1 - Renderização única\n2 - Lote via ZIP\nDigite 1 ou 2: ").strip()

# 📁 Upload do(s) vídeo(s) base
if modo == "1":
    print("\n▶️ Upload do vídeo base:")
    uploaded = files.upload()
    base_paths = list(uploaded.keys())

elif modo == "2":
    print("\n📆 Upload do arquivo ZIP com vídeos base:")
    zip_upload = files.upload()
    zip_name = list(zip_upload.keys())[0]

    with ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall("inputs")

    # Caminhos absolutos de todos os vídeos dentro do ZIP (inclusive subpastas)
    base_paths = []
    for root, _, files_in_dir in os.walk("inputs"):
        for file in files_in_dir:
            if file.lower().endswith(".mp4"):
                base_paths.append(os.path.join(root, file))

else:
    raise ValueError("Modo inválido. Digite 1 ou 2.")

# 🎥 Upload do vídeo de sobreposição
print("\n▶️ Upload do vídeo de sobreposição:")
overlay_upload = files.upload()
overlay_name = list(overlay_upload.keys())[0]

# ⏳ Definir tempo final para sobreposição
dur = input("\nQuantos segundos finais devem ser substituídos pela sobreposição? (ex: 5, 6...): ")
overlay_seconds = int(dur.strip())

# 🎨 Carregar o clipe de sobreposição
overlay_clip = VideoFileClip(overlay_name)

# ⚖️ Redimensionar overlay uma vez (se necessário)
def ajustar_overlay_size(base_clip, overlay):
    return overlay.resize(base_clip.size) if overlay.size != base_clip.size else overlay

# ✅ Processar cada vídeo base
renderizados = []
data_str = datetime.now().strftime("%Y-%m-%d")

for base_path in base_paths:
    try:
        base_clip = VideoFileClip(base_path)
        corte = max(0, base_clip.duration - overlay_seconds)
        base_sem_final = base_clip.subclip(0, corte)

        overlay_redimensionado = ajustar_overlay_size(base_clip, overlay_clip)

        final = concatenate_videoclips([base_sem_final, overlay_redimensionado])

        # Gerar nome e caminho
        base_nome = os.path.splitext(os.path.basename(base_path))[0]
        relative_path = os.path.relpath(base_path, "inputs")
        final_path = os.path.join("outputs", relative_path)
        final_dir = os.path.dirname(final_path)
        os.makedirs(final_dir, exist_ok=True)

        final_output_path = os.path.join(final_dir, f"{base_nome}__RENDERIZADO__{data_str}.mp4")
        final.write_videofile(final_output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

        renderizados.append(final_output_path)

    except Exception as e:
        print(f"Erro ao processar {base_path}: {e}")

# 📆 Compactar resultado final para download
output_zip = f"renderizados_{data_str}.zip"
shutil.make_archive(output_zip.replace(".zip", ""), 'zip', "outputs")

print("\n📂 Processamento finalizado!")
files.download(output_zip)  # Clique para baixar

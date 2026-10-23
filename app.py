import os
import io
import time
import streamlit as st
from PIL import Image
from huggingface_hub import InferenceClient

# =========================================================
# STUDIO AI — FOTO AI & VIDEO AI
# Aplikasi mandiri untuk Streamlit Cloud
# =========================================================

st.set_page_config(
    page_title="Studio AI",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- KONFIGURASI ----------
IMAGE_MODEL = "black-forest-labs/FLUX.1-dev"
VIDEO_MODEL = "Wan-AI/Wan2.2-TI2V-5B"

def get_token():
    """Ambil token dari Streamlit Secrets atau environment."""
    token = os.environ.get("HF_TOKEN", "")
    try:
        token = st.secrets.get("HF_TOKEN", token)
    except Exception:
        pass
    return str(token).strip()

# ---------- DESAIN ----------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at top left,
        rgba(91, 57, 180, .24), transparent 42%),
        linear-gradient(145deg, #0b1020, #111827 55%, #17122b);
    color: #f8fafc;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 30px;
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 24px;
    background: linear-gradient(120deg,
        rgba(106,76,255,.30),
        rgba(20,184,166,.12),
        rgba(255,255,255,.035));
    margin-bottom: 24px;
}
.hero h1 {
    font-size: clamp(2rem, 5vw, 3.2rem);
    margin-bottom: 8px;
    font-weight: 850;
}
.hero p { color: #cbd5e1; font-size: 1.05rem; }
div[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid rgba(255,255,255,.09);
}
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.045);
    padding: 16px;
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 16px;
}
.stButton > button {
    border: 0;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
    background: linear-gradient(90deg, #7657ff, #4f8cff);
    color: white;
}
.stButton > button:hover {
    border: 1px solid #a5b4fc;
    color: white;
    filter: brightness(1.12);
}
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: #151c2e;
    color: white;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 700;
}
.small-note {
    color: #94a3b8;
    font-size: .85rem;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "gallery" not in st.session_state:
    st.session_state.gallery = []

if "generated_count" not in st.session_state:
    st.session_state.generated_count = 0

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## 🎨 STUDIO AI")
    st.caption("Creative AI Workspace")
    page = st.radio(
        "MENU UTAMA",
        ["🏠 Dashboard", "🖼️ Foto AI", "🎬 Video AI", "🗂️ Galeri", "⚙️ Pengaturan"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**Status API**")
    if get_token():
        st.success("Token API tersedia")
    else:
        st.warning("Token API belum diatur")
    st.caption("Gunakan token pribadi. Jangan bagikan token kepada orang lain.")

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <h1>✨ Studio AI</h1>
    <p>Ubah ide menjadi visual. Buat gambar kreatif dan video AI
    langsung dari browser, tanpa memasang model AI di komputer.</p>
</div>
""", unsafe_allow_html=True)

# ---------- DASHBOARD ----------
if page == "🏠 Dashboard":
    c1, c2, c3 = st.columns(3)
    c1.metric("🖼️ Foto AI", "Tersedia")
    c2.metric("🎬 Video AI", "Tersedia")
    c3.metric("✨ Karya sesi ini", st.session_state.generated_count)

    st.markdown("### Mulai berkarya")
    left, right = st.columns(2)

    with left:
        st.markdown("#### 🖼️ Foto AI")
        st.write("Buat visual produk, potret, poster, ilustrasi, dan gambar sinematik.")
        if st.button("Buka Foto AI", use_container_width=True):
            st.session_state.menu_redirect = "🖼️ Foto AI"
            st.rerun()

    with right:
        st.markdown("#### 🎬 Video AI")
        st.write("Buat adegan video berdasarkan deskripsi dan gerakan yang kamu inginkan.")
        if st.button("Buka Video AI", use_container_width=True):
            st.session_state.menu_redirect = "🎬 Video AI"
            st.rerun()

    st.info(
        "Penting: pembuatan media membutuhkan token API dan akses "
        "ke model/provider. Penggunaan dapat dikenakan biaya."
    )

# Navigasi tombol dashboard
if "menu_redirect" in st.session_state:
    redirect = st.session_state.pop("menu_redirect")
    st.info(f"Pilih menu **{redirect}** pada sidebar untuk melanjutkan.")

# ---------- FOTO AI ----------
elif page == "🖼️ Foto AI":
    st.markdown("## 🖼️ Studio Foto AI")
    st.write("Jelaskan gambar yang ingin kamu buat sedetail mungkin.")

    with st.form("image_form"):
        prompt = st.text_area(
            "Deskripsi gambar",
            placeholder=(
                "Contoh: Foto iklan kopi susu dingin dalam gelas bening, "
                "embun pada gelas, pencahayaan studio profesional, "
                "latar cokelat elegan, fotografi produk realistis."
            ),
            height=140,
        )

        col1, col2 = st.columns(2)
        with col1:
            style = st.selectbox(
                "Gaya gambar",
                [
                    "Realistis / Fotografi",
                    "Sinematik",
                    "Iklan Produk",
                    "Ilustrasi Digital",
                    "Fantasi",
                    "Anime",
                ],
            )
        with col2:
            ratio = st.selectbox(
                "Rasio gambar",
                ["Persegi 1:1", "Portrait 2:3", "Landscape 3:2"],
            )

        negative = st.text_input(
            "Hal yang dihindari (opsional)",
            placeholder="misalnya: blur, watermark, teks acak",
        )

        submit_image = st.form_submit_button(
            "✨ GENERATE FOTO AI",
            use_container_width=True,
        )

    if submit_image:
        token = get_token()

        if not token:
            st.error(
                "Token belum diatur. Buka Pengaturan untuk petunjuk "
                "mendapatkan dan memasang HF_TOKEN."
            )
        elif not prompt.strip():
            st.warning("Masukkan deskripsi gambar terlebih dahulu.")
        else:
            style_map = {
                "Realistis / Fotografi": "photorealistic photography, realistic details",
                "Sinematik": "cinematic composition, dramatic lighting, film still",
                "Iklan Produk": "professional commercial product photography, premium advertising",
                "Ilustrasi Digital": "high quality digital illustration, detailed artwork",
                "Fantasi": "beautiful fantasy art, imaginative atmosphere, intricate details",
                "Anime": "high quality anime illustration, detailed anime art",
            }

            full_prompt = (
                f"{prompt.strip()}. Style: {style_map[style]}. "
                "High quality, carefully composed."
            )

            dimensions = {
                "Persegi 1:1": (1024, 1024),
                "Portrait 2:3": (768, 1152),
                "Landscape 3:2": (1152, 768),
            }
            width, height = dimensions[ratio]

            with st.spinner(
                "Sedang membuat gambar AI. Tunggu beberapa saat..."
            ):
                try:
                    client = InferenceClient(
                        api_key=token,
                        timeout=180,
                    )

                    kwargs = {
                        "model": IMAGE_MODEL,
                        "width": width,
                        "height": height,
                    }
                    if negative.strip():
                        kwargs["negative_prompt"] = negative.strip()

                    try:
                        result = client.text_to_image(
                            full_prompt, **kwargs
                        )
                    except Exception as first_error:
                        # Beberapa provider tidak mendukung ukuran khusus.
                        # Coba sekali lagi dengan ukuran default model.
                        if "width" in str(first_error).lower() or \
                           "height" in str(first_error).lower() or \
                           "parameter" in str(first_error).lower():
                            result = client.text_to_image(
                                full_prompt,
                                model=IMAGE_MODEL,
                            )
                        else:
                            raise

                    buffer = io.BytesIO()
                    result.save(buffer, format="PNG")
                    image_bytes = buffer.getvalue()

                    st.image(
                        image_bytes,
                        caption="Hasil Foto AI",
                        use_container_width=True,
                    )

                    st.download_button(
                        "⬇️ Download Foto PNG",
                        data=image_bytes,
                        file_name=f"studio_ai_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True,
                    )

                    st.session_state.gallery.insert(0, {
                        "type": "Foto AI",
                        "prompt": prompt,
                        "data": image_bytes,
                        "mime": "image/png",
                        "filename": f"studio_ai_{int(time.time())}.png",
                    })
                    st.session_state.generated_count += 1
                    st.success("Gambar berhasil dibuat.")

                except Exception as e:
                    st.error("Foto AI gagal dibuat.")
                    st.warning(
                        "Periksa token, saldo/izin inference, nama model, "
                        "dan ketersediaan provider. Detail: " + str(e)[:900]
                    )

# ---------- VIDEO AI ----------
elif page == "🎬 Video AI":
    st.markdown("## 🎬 Studio Video AI")
    st.write(
        "Buat video dari teks. Deskripsikan subjek, gerakan, suasana, "
        "dan gerakan kamera."
    )

    with st.form("video_form"):
        video_prompt = st.text_area(
            "Deskripsi adegan video",
            placeholder=(
                "Contoh: Sebuah botol minuman dingin di atas meja kayu, "
                "kamera bergerak perlahan mendekat, embun air berkilau, "
                "cahaya matahari sore, gaya iklan produk premium."
            ),
            height=150,
        )

        motion = st.selectbox(
            "Gerakan kamera",
            [
                "Gerakan kamera natural",
                "Kamera perlahan mendekat",
                "Kamera bergerak menjauh",
                "Kamera bergerak menyamping",
                "Sudut pandang sinematik",
            ],
        )

        video_style = st.selectbox(
            "Gaya video",
            [
                "Realistis",
                "Sinematik",
                "Iklan Produk",
                "Fantasi",
            ],
        )

        submit_video = st.form_submit_button(
            "🎬 GENERATE VIDEO AI",
            use_container_width=True,
        )

    if submit_video:
        token = get_token()

        if not token:
            st.error(
                "Token belum diatur. Buka Pengaturan untuk petunjuk "
                "mendapatkan dan memasang HF_TOKEN."
            )
        elif not video_prompt.strip():
            st.warning("Masukkan deskripsi video terlebih dahulu.")
        else:
            full_video_prompt = (
                f"{video_prompt.strip()}. "
                f"Camera movement: {motion}. Visual style: {video_style}. "
                "Smooth motion, coherent scene, high visual quality."
            )

            with st.spinner(
                "Video AI sedang diproses. Proses dapat memakan waktu "
                "beberapa menit dan tergantung provider."
            ):
                try:
                    client = InferenceClient(
                        provider="fal-ai",
                        api_key=token,
                        timeout=600,
                    )

                    video_result = client.text_to_video(
                        full_video_prompt,
                        model=VIDEO_MODEL,
                    )

                    if hasattr(video_result, "read"):
                        video_bytes = video_result.read()
                    elif isinstance(video_result, bytes):
                        video_bytes = video_result
                    else:
                        video_bytes = bytes(video_result)

                    if not video_bytes:
                        raise ValueError("Provider mengembalikan video kosong.")

                    filename = f"studio_ai_video_{int(time.time())}.mp4"

                    st.video(video_bytes)
                    st.download_button(
                        "⬇️ Download Video",
                        data=video_bytes,
                        file_name=filename,
                        mime="video/mp4",
                        use_container_width=True,
                    )

                    st.session_state.gallery.insert(0, {
                        "type": "Video AI",
                        "prompt": video_prompt,
                        "data": video_bytes,
                        "mime": "video/mp4",
                        "filename": filename,
                    })
                    st.session_state.generated_count += 1
                    st.success("Video berhasil dibuat.")

                except Exception as e:
                    st.error("Video AI gagal dibuat.")
                    st.warning(
                        "Periksa saldo dan akses provider fal-ai, token, "
                        "ketersediaan model, serta batas waktu provider. "
                        "Detail: " + str(e)[:900]
                    )

# ---------- GALERI ----------
elif page == "🗂️ Galeri":
    st.markdown("## 🗂️ Galeri Karya")
    st.caption(
        "Karya tersimpan sementara selama sesi aplikasi aktif. "
        "Galeri ini belum menjadi penyimpanan permanen."
    )

    gallery = st.session_state.gallery

    if not gallery:
        st.info("Belum ada karya. Mulai dari menu Foto AI atau Video AI.")
    else:
        st.write(f"Jumlah karya: **{len(gallery)}**")

        for index, item in enumerate(gallery):
            with st.container(border=True):
                st.markdown(f"**{item['type']} — Karya {len(gallery)-index}**")
                st.caption(item["prompt"])

                if item["mime"].startswith("image/"):
                    st.image(item["data"], use_container_width=True)
                else:
                    st.video(item["data"])

                st.download_button(
                    "⬇️ Download",
                    data=item["data"],
                    file_name=item["filename"],
                    mime=item["mime"],
                    key=f"download_gallery_{index}",
                )

        if st.button("🗑️ Kosongkan Galeri"):
            st.session_state.gallery = []
            st.rerun()

# ---------- PENGATURAN ----------
elif page == "⚙️ Pengaturan":
    st.markdown("## ⚙️ Pengaturan API")
    st.write(
        "Studio AI menggunakan Hugging Face Inference Providers untuk "
        "menghubungkan aplikasi dengan model gambar dan video."
    )

    st.markdown("### Langkah 1 — Buat token")
    st.markdown(
        "1. Buka [Hugging Face Token Settings]"
        "(https://huggingface.co/settings/tokens).\n"
        "2. Buat token baru dengan izin **Make calls to Inference Providers**.\n"
        "3. Salin token dan simpan secara rahasia."
    )

    st.markdown("### Langkah 2 — Simpan token di Streamlit Cloud")
    st.markdown(
        "1. Buka aplikasi di Streamlit Cloud.\n"
        "2. Masuk ke **Settings → Secrets**.\n"
        "3. Masukkan konfigurasi berikut:"
    )

    st.code('HF_TOKEN = "hf_token_pribadi_kamu"', language="toml")

    st.warning(
        "Ganti teks contoh dengan token asli. Jangan masukkan token ke "
        "GitHub, jangan kirim token di chat, dan jangan tampilkan token "
        "di halaman aplikasi."
    )

    st.markdown("### Model yang digunakan")
    st.code(
        f"Foto AI: {IMAGE_MODEL}\nVideo AI: {VIDEO_MODEL}\n"
        "Provider video: fal-ai",
        language="text",
    )

    st.markdown("### Informasi biaya")
    st.write(
        "Hosting aplikasi dan biaya generasi AI adalah dua hal berbeda. "
        "Inference Providers dapat memerlukan kredit berbayar. "
        "Periksa harga, akses model, dan pemakaian di akun penyedia "
        "sebelum membuat banyak gambar atau video."
    )

    st.markdown(
        "[Dokumentasi Inference Providers]"
        "(https://huggingface.co/docs/inference-providers/index)"
    )

# ---------- FOOTER ----------
st.divider()
st.markdown(
    '<p class="small-note" style="text-align:center">'
    'STUDIO AI • Creative Workspace • Powered by Streamlit and AI inference'
    '</p>',
    unsafe_allow_html=True,
)

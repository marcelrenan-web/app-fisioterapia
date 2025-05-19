import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import whisper
import numpy as np
from datetime import datetime

# Carrega modelo Whisper
model = whisper.load_model("base")  # Pode usar "tiny" para mais leve

# Página inicial
st.set_page_config(page_title="Ficha de Atendimento - Fisioterapia", layout="centered")
st.title("🩺 Ficha de Atendimento - Fisioterapia com IA")

# Correções de termos comuns
def corrigir_termos(texto):
    correcoes = {
        "tendinite": "tendinite",
        "cervicalgia": "cervicalgia",
        "lombar": "região lombar",
        "reabilitação funcional": "reabilitação funcional",
        "fisioterapia do ombro": "fisioterapia de ombro",
        "dor nas costas": "algia na coluna",
    }
    for errado, certo in correcoes.items():
        texto = texto.replace(errado, certo)
    return texto

# Session state para salvar a transcrição
if "transcricao" not in st.session_state:
    st.session_state.transcricao = ""

# Processador de áudio
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype(np.float32).tobytes()
        self.buffer += pcm

        if len(self.buffer) > 32000 * 5:  # 5 segundos
            audio_np = np.frombuffer(self.buffer, np.float32)
            audio_np = whisper.pad_or_trim(audio_np)
            mel = whisper.log_mel_spectrogram(audio_np).to(model.device)
            options = whisper.DecodingOptions(language="pt", fp16=False)
            result = whisper.decode(model, mel, options)
            st.session_state.transcricao += corrigir_termos(result.text) + " "
            self.buffer = b""
        return frame

# Stream do microfone
st.subheader("🎤 Fale e veja o texto ao vivo:")
webrtc_streamer(
    key="microfone",
    mode="SENDONLY",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# Exibir transcrição atual
st.text_area("📝 Texto reconhecido:", st.session_state.transcricao, height=200)

# Formulário da ficha de atendimento
st.subheader("📋 Preencha os dados do atendimento")
with st.form("formulario_ficha"):
    nome = st.text_input("Nome do paciente")
    idade = st.number_input("Idade", min_value=0, max_value=120)
    data_atendimento = st.date_input("Data do atendimento", value=datetime.today())
    sintomas = st.text_area("Relato do paciente", value=st.session_state.transcricao)
    diagnostico = st.text_area("Diagnóstico clínico")
    conduta = st.text_area("Conduta adotada")
    enviado = st.form_submit_button("Salvar ficha")

    if enviado:
        st.success("✅ Ficha salva com sucesso!")
        st.write("---")
        st.markdown(f"""
        **👤 Paciente:** {nome}  
        **📅 Data:** {data_atendimento.strftime('%d/%m/%Y')}  
        **🎂 Idade:** {int(idade)} anos  
        **🗣️ Relato:** {sintomas}  
        **🩺 Diagnóstico:** {diagnostico}  
        **📝 Conduta:** {conduta}
        """)

 

 

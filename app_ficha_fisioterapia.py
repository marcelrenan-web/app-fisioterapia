import streamlit as st
import speech_recognition as sr
from datetime import datetime
import PyPDF2

# Configuração da página
st.set_page_config(page_title="Ficha de Atendimento - Fisioterapia", layout="centered")
st.title("🩺 Ficha de Atendimento - Fisioterapia com IA")

# Função para aplicar correções automáticas
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

# Estado inicial do texto
if "texto_extraido" not in st.session_state:
    st.session_state.texto_extraido = ""

# Gravação de voz
st.subheader("🎤 Registrar atendimento por voz")
if st.button("Iniciar gravação"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("Fale agora...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            texto = recognizer.recognize_google(audio, language="pt-BR")
            texto_corrigido = corrigir_termos(texto)
            st.session_state.texto_extraido = texto_corrigido
            st.success("Texto reconhecido e corrigido com sucesso!")
        except sr.UnknownValueError:
            st.error("Não foi possível reconhecer o que foi dito.")
        except sr.RequestError:
            st.error("Erro ao se conectar ao serviço de reconhecimento de voz.")
        except sr.WaitTimeoutError:
            st.error("Tempo de escuta excedido. Tente novamente.")

# Exibição do texto reconhecido
if st.session_state.texto_extraido:
    st.write("📝 Texto reconhecido e corrigido:")
    st.write(f"> {st.session_state.texto_extraido}")

# Upload de PDF
st.subheader("📄 Extrair texto de PDF")
uploaded_file = st.file_uploader("Envie um arquivo PDF com o atendimento", type="pdf")
if uploaded_file is not None:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        texto_pdf = ""
        for page in pdf_reader.pages:
            texto_pdf += page.extract_text()
        texto_corrigido = corrigir_termos(texto_pdf)
        st.session_state.texto_extraido = texto_corrigido
        st.success("Texto extraído e corrigido com sucesso!")
    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")

# Formulário da ficha de atendimento
with st.form("formulario_ficha"):
    nome = st.text_input("Nome do paciente")
    idade = st.number_input("Idade", min_value=0, max_value=120)
    data_atendimento = st.date_input("Data do atendimento", value=datetime.today())
    sintomas = st.text_area("Relato do paciente (pode colar o texto reconhecido)", value=st.session_state.texto_extraido)
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

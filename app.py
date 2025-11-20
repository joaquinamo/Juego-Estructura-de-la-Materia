import streamlit as st
import pandas as pd
import time
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Quantum Rush",
    page_icon="⚛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS (CYBERPUNK / LABORATORIO) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .main-card {
        background: linear-gradient(145deg, #1e1e24, #2a2a35);
        border: 1px solid #454555;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        font-size: 22px;
        font-weight: 500;
        color: #ffffff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        margin-bottom: 20px;
    }
    .stat-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }
    .combo-active {
        color: #ffd700;
        font-weight: bold;
        text-shadow: 0 0 10px #ffd700;
    }
    .justification-box {
        background-color: #1c2329;
        border-left: 5px solid #00d4ff;
        padding: 15px;
        margin-top: 15px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGAR DATOS ---
@st.cache_data
def load_data():
    filename = "Preguntas V o F estructura de la materia - N.º,Afirmación,Respuesta,Justificac.csv"
    try:
        # Ajustamos para leer correctamente el CSV subido
        df = pd.read_csv(filename)
        # Normalizar nombres de columnas por si acaso hay espacios extra
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"⚠️ Error: No encuentro el archivo '{filename}'.")
        return pd.DataFrame()

df = load_data()

# --- ESTADO DEL JUEGO (SESSION STATE) ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'lives' not in st.session_state: st.session_state.lives = 100  # Barra de vida 0-100
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'current_q' not in st.session_state: st.session_state.current_q = None
if 'answered' not in st.session_state: st.session_state.answered = False
if 'feedback_type' not in st.session_state: st.session_state.feedback_type = None # 'success' or 'error'
if 'points_gained' not in st.session_state: st.session_state.points_gained = ""
if 'game_topic' not in st.session_state: st.session_state.game_topic = "Todos"

# --- FUNCIÓN PROCESAR RESPUESTA (MOVÍ ESTA FUNCIÓN ARRIBA) ---
def process_answer(is_correct):
    if is_correct:
        # Cálculo de puntos
        base_points = 100
        multiplier = 2 if st.session_state.streak >= 3 else 1
        points = base_points * multiplier
        
        st.session_state.score += points
        st.session_state.streak += 1
        st.session_state.feedback_type = 'success'
        st.session_state.points_gained = f"+{points}"
        if st.session_state.lives < 100:
            st.session_state.lives = min(100, st.session_state.lives + 5) # Recuperar vida
        st.balloons()
    else:
        st.session_state.lives -= 20 # Daño
        st.session_state.streak = 0
        st.session_state.feedback_type = 'error'
    
    st.session_state.answered = True
    st.rerun()

# --- BARRA LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración del Reactor")
    if not df.empty:
        temas = ["Todos"] + list(df['Tema'].unique())
        selected_topic = st.selectbox("Seleccionar Tema:", temas)
        if selected_topic != st.session_state.game_topic:
            st.session_state.game_topic = selected_topic
            st.session_state.current_q = None # Resetear pregunta al cambiar tema
            st.rerun()
    
    if st.button("Reiniciar Juego"):
        st.session_state.score = 0
        st.session_state.lives = 100
        st.session_state.streak = 0
        st.session_state.answered = False
        st.session_state.current_q = None
        st.rerun()

# --- LÓGICA DE SELECCIÓN DE PREGUNTA ---
def get_new_question():
    if st.session_state.game_topic == "Todos":
        return df.sample(1).iloc[0]
    else:
        filtered_df = df[df['Tema'] == st.session_state.game_topic]
        if filtered_df.empty:
            st.warning("No hay preguntas para este tema.")
            return df.sample(1).iloc[0]
        return filtered_df.sample(1).iloc[0]

if st.session_state.current_q is None and not df.empty:
    st.session_state.current_q = get_new_question()

# --- INTERFAZ PRINCIPAL ---
st.title("⚛️ Quantum Rush")

# 1. Panel de Estadísticas
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='stat-box'>🏆 Puntos: {st.session_state.score}</div>", unsafe_allow_html=True)
with col2:
    # Barra de vida visual
    life_color = "green" if st.session_state.lives > 50 else "orange" if st.session_state.lives > 20 else "red"
    st.markdown(f"<div class='stat-box'>❤️ Integridad: {st.session_state.lives}%</div>", unsafe_allow_html=True)
    st.progress(st.session_state.lives / 100)
with col3:
    combo_class = "combo-active" if st.session_state.streak >= 3 else ""
    emoji = "🔥" if st.session_state.streak >= 3 else "⚡"
    st.markdown(f"<div class='stat-box {combo_class}'>{emoji} Racha: {st.session_state.streak}</div>", unsafe_allow_html=True)

st.divider()

# 2. Estado Game Over
if st.session_state.lives <= 0:
    st.markdown("## 💥 CRITICAL FAILURE: FUSIÓN DEL NÚCLEO")
    st.error("El sistema se ha desestabilizado. Has perdido toda la integridad del átomo.")
    st.image("https://media.giphy.com/media/3oKIPwoeGErMmaI43S/giphy.gif") # Gif de explosión o estática
    if st.button("🛠️ Reparar Reactor (Reiniciar)", type="primary"):
        st.session_state.score = 0
        st.session_state.lives = 100
        st.session_state.streak = 0
        st.session_state.answered = False
        st.session_state.current_q = None
        st.rerun()

# 3. Juego Activo
elif st.session_state.current_q is not None:
    q = st.session_state.current_q
    
    # Tarjeta de Pregunta
    st.markdown(f"""
    <div class='main-card'>
        {q['Afirmación']}
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de Respuesta
    if not st.session_state.answered:
        c1, c2 = st.columns(2)
        if c1.button("VERDADERO", use_container_width=True):
            user_ans = "Verdadero"
            correct = str(q['Respuesta']).strip().lower() == "verdadero"
            process_answer(correct)
        
        if c2.button("FALSO", use_container_width=True):
            user_ans = "Falso"
            correct = str(q['Respuesta']).strip().lower() == "falso"
            process_answer(correct)
            
    # Feedback y Justificación
    else:
        if st.session_state.feedback_type == 'success':
            st.success(f"¡CORRECTO! {st.session_state.points_gained} Puntos")
            if st.session_state.streak >= 3:
                st.caption("🚀 ¡COMBO ACTIVADO! PUNTOS DOBLES")
        else:
            st.error("❌ INCORRECTO. Integridad del núcleo comprometida.")
        
        # Mostrar justificación didáctica
        st.markdown(f"""
        <div class='justification-box'>
            <strong>📖 Explicación:</strong> {q['Justificación']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Siguiente Nivel ➡️", type="primary"):
            st.session_state.answered = False
            st.session_state.current_q = get_new_question()
            st.rerun()
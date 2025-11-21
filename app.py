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

# --- ESTILOS CSS (MODO CLARO / AULA) ---
st.markdown("""
    <style>
    /* Fondo general blanco */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    /* Tarjeta de pregunta grande y clara */
    .main-card {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        font-size: 26px; /* Letra más grande para proyector */
        font-weight: 600;
        color: #212529;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 25px;
    }
    /* Cajas de estadísticas */
    .stat-box {
        background-color: #eef2f7;
        border: 1px solid #ced4da;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        font-size: 18px;
        color: #000000;
        font-weight: bold;
    }
    /* Estilo para racha activa */
    .combo-active {
        background-color: #fff3cd; /* Fondo amarillo claro */
        color: #856404;
        border: 2px solid #ffeeba;
    }
    /* Caja de justificación */
    .justification-box {
        background-color: #d1ecf1; /* Azul muy clarito */
        color: #0c5460; /* Texto azul oscuro */
        border-left: 6px solid #17a2b8;
        padding: 20px;
        margin-top: 20px;
        border-radius: 5px;
        font-size: 20px; /* Letra grande */
    }
    /* Botones más grandes */
    .stButton button {
        font-size: 20px !important;
        font-weight: bold !important;
        padding: 15px !important;
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
        # Normalizar nombres de columnas
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"⚠️ Error: No encuentro el archivo '{filename}'.")
        return pd.DataFrame()

df = load_data()

# --- ESTADO DEL JUEGO ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'lives' not in st.session_state: st.session_state.lives = 100
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'current_q' not in st.session_state: st.session_state.current_q = None
if 'answered' not in st.session_state: st.session_state.answered = False
if 'feedback_type' not in st.session_state: st.session_state.feedback_type = None 
if 'points_gained' not in st.session_state: st.session_state.points_gained = ""
if 'game_topic' not in st.session_state: st.session_state.game_topic = "Todos"

# --- FUNCIÓN PROCESAR RESPUESTA ---
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
            st.session_state.lives = min(100, st.session_state.lives + 5)
        st.balloons()
    else:
        st.session_state.lives -= 20
        st.session_state.streak = 0
        st.session_state.feedback_type = 'error'
    
    st.session_state.answered = True
    st.rerun()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    if not df.empty:
        temas = ["Todos"] + list(df['Tema'].unique())
        selected_topic = st.selectbox("Filtrar por Tema:", temas)
        if selected_topic != st.session_state.game_topic:
            st.session_state.game_topic = selected_topic
            st.session_state.current_q = None
            st.rerun()
    
    if st.button("🔄 Reiniciar Juego"):
        st.session_state.score = 0
        st.session_state.lives = 100
        st.session_state.streak = 0
        st.session_state.answered = False
        st.session_state.current_q = None
        st.rerun()

# --- LÓGICA DE SELECCIÓN ---
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
st.title("⚛️ Quantum Rush: Clase de Física y Química")

# 1. Panel de Estadísticas
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='stat-box'>🏆 Puntos: {st.session_state.score}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-box'>❤️ Energía: {st.session_state.lives}%</div>", unsafe_allow_html=True)
    st.progress(st.session_state.lives / 100)
with col3:
    combo_class = "combo-active" if st.session_state.streak >= 3 else ""
    emoji = "🔥" if st.session_state.streak >= 3 else "⚡"
    st.markdown(f"<div class='stat-box {combo_class}'>{emoji} Racha: {st.session_state.streak}</div>", unsafe_allow_html=True)

st.divider()

# 2. Estado Game Over
if st.session_state.lives <= 0:
    st.error("⚠️ EL SISTEMA SE HA DETENIDO. Juego Terminado.")
    if st.button("🔄 Empezar de nuevo", type="primary"):
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
        # Usamos colores primarios y secundarios para diferenciar
        if c1.button("VERDADERO ✅", use_container_width=True, type="primary"):
            user_ans = "Verdadero"
            correct = str(q['Respuesta']).strip().lower() == "verdadero"
            process_answer(correct)
        
        if c2.button("FALSO ❌", use_container_width=True):
            user_ans = "Falso"
            correct = str(q['Respuesta']).strip().lower() == "falso"
            process_answer(correct)
            
    # Feedback y Justificación
    else:
        if st.session_state.feedback_type == 'success':
            st.success(f"¡MUY BIEN! Has ganado {st.session_state.points_gained} puntos.")
        else:
            st.error("RESPUESTA INCORRECTA. ¡Ánimo para la siguiente!")
        
        # Mostrar justificación didáctica
        st.markdown(f"""
        <div class='justification-box'>
            <strong>💡 Explicación:</strong><br>
            {q['Justificación']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Siguiente Pregunta ➡️", type="primary"):
            st.session_state.answered = False
            st.session_state.current_q = get_new_question()
            st.rerun()

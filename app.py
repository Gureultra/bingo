import streamlit as st
import datetime
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Bingo Ciclista Gure",
    page_icon="🚴",
    layout="centered"
)

# --- ESTILOS CSS (MODO CLARO - IDENTIDAD GURE) ---
st.markdown("""
    <style>
    /* Fondo Blanco y Textos Oscuros */
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
    }
    
    /* Títulos */
    h1 {
        font-family: 'Arial Black', sans-serif;
        font-style: italic;
        color: #000000 !important;
        text-transform: uppercase;
        margin-bottom: 0px;
    }
    h1 span {
        color: #DC2626; /* Rojo Gure */
    }
    
    /* Subtítulos */
    .caption-text {
        font-size: 1.1em;
        color: #4b5563;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Botones Rojos Estilo Gure */
    .stButton > button {
        background-color: #DC2626;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.2s;
        box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.2);
    }
    .stButton > button:hover {
        background-color: #b91c1c; /* Rojo más oscuro */
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(220, 38, 38, 0.3);
    }
    
    /* Estilos para las tarjetas de Reto (Cards) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    
    /* Texto de descripción del reto */
    .challenge-desc {
        font-size: 0.85em;
        color: #6b7280;
        margin-bottom: 10px;
        line-height: 1.2;
        min-height: 2.4em; /* Altura uniforme */
    }
    
    /* Mensajes de éxito */
    .stSuccess {
        background-color: #ecfdf5;
        color: #065f46;
        border: none;
        font-size: 0.8em;
    }
    .stError {
        background-color: #fef2f2;
        color: #991b1b;
        border: none;
        font-size: 0.8em;
    }
    
    /* Input de archivo más discreto */
    div[data-testid="stFileUploader"] section {
        padding: 10px;
        background-color: #f9fafb;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATOS DEL BINGO (16 RETOS) ---
if 'challenges' not in st.session_state:
    st.session_state.challenges = [
        # Fila 1
        {"id": 1, "title": "El Panadero", "desc": "Terminar antes de las 08:00 AM", "icon": "☀️", "completed": False, "rules": {"maxTime": "08:00"}},
        {"id": 2, "title": "El Vampiro", "desc": "Empezar después de las 21:00 PM", "icon": "🌙", "completed": False, "rules": {"minTime": "21:00"}},
        {"id": 3, "title": "Doblete Finde", "desc": "Entrenar Sábado y Domingo", "icon": "📅", "completed": False, "rules": {}},
        {"id": 4, "title": "El Expreso", "desc": "< 45 min a IF ≥ 1.0 (Full Gas)", "icon": "⚡", "completed": False, "rules": {"maxDuration": 45, "minIF": 1.0}},
        
        # Fila 2
        {"id": 5, "title": "Viva Galicia", "desc": "Ruta por tierras gallegas", "icon": "🗺️", "completed": False, "rules": {}},
        {"id": 6, "title": "Ruta Bkool", "desc": "Completar ruta Bkool en Rouvy", "icon": "📺", "completed": False, "rules": {}},
        {"id": 7, "title": "La Clásica", "desc": "Tramo mítico o Monumento", "icon": "🏆", "completed": False, "rules": {}},
        {"id": 8, "title": "El Exótico", "desc": "Ruta en continente distinto", "icon": "🌍", "completed": False, "rules": {}},
        
        # Fila 3
        {"id": 9, "title": "El Molinillo", "desc": "Cadencia media > 85 rpm", "icon": "🔄", "completed": False, "rules": {}},
        {"id": 10, "title": "Zona Confort", "desc": ">1h sin pasar de Zona 2", "icon": "❤️", "completed": False, "rules": {"minDuration": 60}},
        {"id": 11, "title": "El Muro", "desc": "Rampa del 14% o superior", "icon": "⛰️", "completed": False, "rules": {"minGradient": 14}},
        {"id": 12, "title": "Capicúa", "desc": "Distancia capicúa (ej: 22.22km)", "icon": "#️⃣", "completed": False, "rules": {}},
        
        # Fila 4
        {"id": 13, "title": "Coffee Ride", "desc": "Foto con café/cerveza", "icon": "☕", "completed": False, "rules": {}},
        {"id": 14, "title": "Grupeta", "desc": "Coincidir con alguien", "icon": "👥", "completed": False, "rules": {}},
        {"id": 15, "title": "Gran Fondo", "desc": "Sesión > 3h seguidas", "icon": "📈", "completed": False, "rules": {"minDuration": 180}},
        {"id": 16, "title": "Los Torreznos", "desc": "Quemar > 1.500 kcal", "icon": "🔥", "completed": False, "rules": {"minCalories": 1500}},
    ]

# --- SIMULADOR DE LECTURA FIT ---
def parse_fit_file_simulated(uploaded_file):
    time.sleep(0.8) # Un poco más rápido para mejorar UX
    seed = sum(ord(c) for c in uploaded_file.name)
    random.seed(seed)
    
    # Generación de datos
    duration = random.randint(30, 240) # minutos
    calories = duration * random.randint(8, 16) # Kcal
    intensity_factor = round(random.uniform(0.6, 1.2), 2) # IF
    max_gradient = random.randint(4, 18) # % Pendiente
    
    # Fecha simulada (Marzo 2026)
    day = random.randint(1, 30)
    hour = random.randint(6, 22)
    simulated_date = datetime.datetime(2026, 3, day, hour, 30)
    
    return {
        "date": simulated_date,
        "duration": duration,
        "calories": calories,
        "if": intensity_factor,
        "gradient": max_gradient
    }

# --- MOTOR DE REGLAS ---
def validate_rules(stats, rules):
    logs = []
    is_valid = True
    
    # 1. Validar Fecha
    if stats['date'].year == 2026 and stats['date'].month == 3:
        logs.append("✅ Fecha correcta")
    else:
        logs.append("⚠️ Fecha incorrecta (Demo)")
        
    # 2. Reglas Específicas
    if "minDuration" in rules:
        if stats['duration'] >= rules['minDuration']:
            logs.append(f"✅ Duración OK ({stats['duration']}m)")
        else:
            logs.append(f"❌ Muy corto ({stats['duration']}m)")
            is_valid = False
            
    if "maxDuration" in rules:
        if stats['duration'] <= rules['maxDuration']:
            logs.append(f"✅ Tiempo OK ({stats['duration']}m)")
        else:
            logs.append(f"❌ Muy largo ({stats['duration']}m)")
            is_valid = False

    if "minCalories" in rules:
        if stats['calories'] >= rules['minCalories']:
            logs.append(f"✅ Kcal OK ({stats['calories']})")
        else:
            logs.append(f"❌ Pocas Kcal ({stats['calories']})")
            is_valid = False
            
    if "minIF" in rules:
        if stats['if'] >= rules['minIF']:
            logs.append(f"✅ IF OK ({stats['if']})")
        else:
            logs.append(f"❌ Falta gas (IF {stats['if']})")
            is_valid = False
            
    if "minGradient" in rules:
        if stats['gradient'] >= rules['minGradient']:
            logs.append(f"✅ Rampa OK ({stats['gradient']}%)")
        else:
            logs.append(f"❌ Muy suave ({stats['gradient']}%)")
            is_valid = False
            
    if "maxTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str < rules['maxTime']:
            logs.append(f"✅ Hora OK ({time_str})")
        else:
             logs.append(f"❌ Tarde ({time_str})")
             is_valid = False

    if "minTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str > rules['minTime']:
            logs.append(f"✅ Hora OK ({time_str})")
        else:
             logs.append(f"❌ Pronto ({time_str})")
             is_valid = False
             
    return is_valid, logs

# --- INTERFAZ GRÁFICA (UI) ---

# Cabecera con Logo GURE
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://gureultra.com/wp-content/uploads/2024/10/GureUltra.png", use_container_width=True)
with col_title:
    st.markdown("<h1>BINGO CICLISTA <span>GURE</span></h1>", unsafe_allow_html=True)
    st.markdown('<p class="caption-text">Un reto para la más Ciclópatas</p>', unsafe_allow_html=True)

st.divider()

# Barra de Progreso
completed_count = sum(1 for c in st.session_state.challenges if c['completed'])
st.progress(completed_count / 16)
col_m1, col_m2 = st.columns(2)
col_m1.metric("Retos Conseguidos", f"{completed_count}/16")
col_m2.metric("Estado", "En curso...")

st.markdown("<br>", unsafe_allow_html=True)

# Grid de Retos (4x4) - VISUALMENTE MEJORADO
rows = [st.session_state.challenges[i:i + 4] for i in range(0, 16, 4)]

for row in rows:
    cols = st.columns(4)
    for idx, challenge in enumerate(row):
        with cols[idx]:
            # Usamos st.container con borde para crear efecto "Tarjeta"
            with st.container(border=True):
                # Cabecera de la tarjeta: Icono y Título
                st.markdown(f"### {challenge['icon']}")
                st.markdown(f"**{challenge['title']}**")
                
                # Descripción siempre visible
                st.markdown(f"<div class='challenge-desc'>{challenge['desc']}</div>", unsafe_allow_html=True)
                
                if challenge['completed']:
                    # Estado Completado
                    st.success(f"✅ Hecho: {challenge.get('date_str', '--/--')}")
                    if st.button("Deshacer", key=f"undo_{challenge['id']}"):
                        challenge['completed'] = False
                        st.rerun()
                else:
                    # Estado Pendiente: Botón desplegable (Expander) para mantener limpieza
                    with st.expander("Validar"):
                        uploaded_file = st.file_uploader("", type=['fit'], key=f"up_{challenge['id']}", label_visibility="collapsed")
                        
                        if uploaded_file is not None:
                            with st.spinner('Analizando...'):
                                stats = parse_fit_file_simulated(uploaded_file)
                                is_valid, logs = validate_rules(stats, challenge['rules'])
                                
                                st.caption(f"📊 {stats['duration']}m | {stats['calories']}kcal")
                                
                                for log in logs:
                                    if "✅" in log: st.caption(f":green[{log}]")
                                    else: st.caption(f":red[{log}]")
                                
                                if is_valid:
                                    if st.button("CONFIRMAR", key=f"btn_{challenge['id']}"):
                                        challenge['completed'] = True
                                        challenge['date_str'] = stats['date'].strftime("%d/%m")
                                        st.balloons()
                                        time.sleep(0.5)
                                        st.rerun()
                                else:
                                    st.error("No válido")

st.divider()

# BOTÓN TELEGRAM ROJO
share_text = f"🚴‍♂️ *BINGO GURE 2026* 🔴⚫ %0A✅ {completed_count}/16 Retos completados."
group_link = "https://t.me/c/GURE_Ultra/50105"

st.markdown(f"""
    <div style="text-align: center;">
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
            Tu progreso: <code style="background: #f3f4f6; color: #1f2937; padding: 4px; border-radius: 4px;">{completed_count}/16 Retos ✅</code>
        </p>
        <a href="{group_link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#DC2626; color:white; padding:14px 24px; border-radius:8px; font-weight:bold; cursor:pointer; display: inline-block; font-size: 16px; box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.3); transition: transform 0.2s;">
                ✈️ Comparte tu avance del reto
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><center><small style='color: #9ca3af;'>© 2026 GURE Ultra Team</small></center>", unsafe_allow_html=True)

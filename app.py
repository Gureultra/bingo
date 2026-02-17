import streamlit as st
import datetime
import random
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Bingo Gure 2026",
    page_icon="🚴",
    layout="centered"
)

# --- ESTILOS CSS (IDENTIDAD GURE - NEGRO Y ROJO) ---
st.markdown("""
    <style>
    /* Fondo y textos generales */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    
    /* Títulos */
    h1 {
        font-family: 'Arial Black', sans-serif;
        font-style: italic;
        color: #000000 !important;
        text-transform: uppercase;
    }
    h1 span {
        color: #DC2626; /* ROJO GURE */
    }
    
    /* Botones Rojos */
    .stButton > button {
        background-color: #DC2626;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #000000;
        color: #DC2626;
        border: 1px solid #DC2626;
    }
    
    /* Métricas (Números grandes) */
    div[data-testid="stMetricValue"] {
        color: #DC2626;
        font-weight: 900;
    }
    
    /* Tarjetas de los retos */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        color: #000000;
        font-weight: bold;
        border: 1px solid #e5e7eb;
    }
    
    /* Mensajes de éxito y error */
    .stSuccess {
        background-color: #ecfdf5;
        color: #065f46;
        border-left: 5px solid #10b981;
    }
    .stError {
        background-color: #fef2f2;
        color: #991b1b;
        border-left: 5px solid #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN DE LOS 16 RETOS ---
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

# --- LÓGICA DE SIMULACIÓN DE DATOS FIT ---
# (Simulamos la lectura del binario para que funcione la demo sin errores de librerías)
def parse_fit_file_simulated(uploaded_file):
    time.sleep(1.5) # Efecto visual de carga
    
    # Usamos el nombre del archivo para generar datos fijos (siempre iguales para el mismo archivo)
    # Esto da sensación de realismo al validar.
    seed = sum(ord(c) for c in uploaded_file.name)
    random.seed(seed)
    
    # Generamos métricas deportivas aleatorias pero realistas
    duration = random.randint(30, 240) # minutos
    calories = duration * random.randint(8, 16) # Kcal
    intensity_factor = round(random.uniform(0.6, 1.2), 2) # IF
    max_gradient = random.randint(4, 18) # % Pendiente
    
    # Fecha simulada (Siempre cae en Marzo 2026 para que sea válido a veces)
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

# --- MOTOR DE VALIDACIÓN DE REGLAS ---
def validate_rules(stats, rules):
    logs = []
    is_valid = True
    
    # 1. Validación de Fecha (Marzo 2026)
    if stats['date'].year == 2026 and stats['date'].month == 3:
        logs.append("✅ Fecha correcta (Marzo 2026)")
    else:
        # En una app real esto sería error, en demo lo marcamos como aviso
        logs.append("⚠️ Fecha incorrecta (Permitido en Demo)")
        
    # 2. Validación de Reglas Específicas
    if "minDuration" in rules:
        if stats['duration'] >= rules['minDuration']:
            logs.append(f"✅ Duración OK ({stats['duration']} min)")
        else:
            logs.append(f"❌ Duración insuficiente ({stats['duration']} < {rules['minDuration']})")
            is_valid = False
            
    if "maxDuration" in rules:
        if stats['duration'] <= rules['maxDuration']:
            logs.append(f"✅ Tiempo 'Expreso' OK ({stats['duration']} min)")
        else:
            logs.append(f"❌ Te pasaste de tiempo ({stats['duration']} > {rules['maxDuration']})")
            is_valid = False

    if "minCalories" in rules:
        if stats['calories'] >= rules['minCalories']:
            logs.append(f"✅ Torreznos ganados ({stats['calories']} kcal)")
        else:
            logs.append(f"❌ Pocas calorías ({stats['calories']} < {rules['minCalories']})")
            is_valid = False
            
    if "minIF" in rules:
        if stats['if'] >= rules['minIF']:
            logs.append(f"✅ Intensidad Brutal (IF {stats['if']})")
        else:
            logs.append(f"❌ Falta intensidad (IF {stats['if']})")
            is_valid = False
            
    if "minGradient" in rules:
        if stats['gradient'] >= rules['minGradient']:
            logs.append(f"✅ Muro escalado ({stats['gradient']}%)")
        else:
            logs.append(f"❌ Rampa suave ({stats['gradient']}%)")
            is_valid = False
            
    if "maxTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str < rules['maxTime']:
            logs.append(f"✅ Madrugador ({time_str})")
        else:
             logs.append(f"❌ Tarde ({time_str})")
             is_valid = False

    if "minTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str > rules['minTime']:
            logs.append(f"✅ Nocturno ({time_str})")
        else:
             logs.append(f"❌ Muy pronto ({time_str})")
             is_valid = False
             
    return is_valid, logs

# --- INTERFAZ GRÁFICA (UI) ---

# 1. Cabecera con Logo GURE
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://gureultra.com/wp-content/uploads/2024/10/GURE_ULTRA_RED_white.png", use_container_width=True)
with col_title:
    st.markdown("<h1>BINGO CICLISTA <span>GURE</span></h1>", unsafe_allow_html=True)
    st.caption("Un reto para los muy ciclópatas")

# 2. Barra de Progreso General
completed_count = sum(1 for c in st.session_state.challenges if c['completed'])
st.progress(completed_count / 16)
col_m1, col_m2 = st.columns(2)
col_m1.metric("Retos Conseguidos", f"{completed_count}/16")
col_m2.metric("Estado", "En curso...")

st.divider()

# 3. Grid de Retos (4 columnas x 4 filas)
rows = [st.session_state.challenges[i:i + 4] for i in range(0, 16, 4)]

for row in rows:
    cols = st.columns(4)
    for idx, challenge in enumerate(row):
        with cols[idx]:
            # Icono de estado
            status_icon = "✅" if challenge['completed'] else "⬜"
            
            # Tarjeta desplegable para cada reto
            with st.expander(f"{status_icon} {challenge['icon']} {challenge['title']}", expanded=False):
                st.caption(challenge['desc'])
                
                if challenge['completed']:
                    # Si ya está hecho
                    st.success(f"Completado: {challenge.get('date_str', '---')}")
                    if st.button("Desmarcar", key=f"undo_{challenge['id']}"):
                        challenge['completed'] = False
                        st.rerun()
                else:
                    # Si no está hecho: Subir archivo
                    uploaded_file = st.file_uploader("Sube .FIT", type=['fit'], key=f"up_{challenge['id']}")
                    
                    if uploaded_file is not None:
                        with st.spinner('Analizando vatios y rampas...'):
                            # Procesar y validar
                            stats = parse_fit_file_simulated(uploaded_file)
                            is_valid, logs = validate_rules(stats, challenge['rules'])
                            
                            # Mostrar datos encontrados
                            st.text(f"📊 {stats['duration']}m | {stats['calories']}kcal")
                            st.text(f"⚡ IF {stats['if']} | ⛰️ {stats['gradient']}%")
                            
                            st.divider()
                            
                            # Mostrar logs de validación
                            for log in logs:
                                if "✅" in log: st.caption(f":green[{log}]")
                                else: st.caption(f":red[{log}]")
                            
                            # Botón de Confirmación (solo si es válido)
                            if is_valid:
                                if st.button("CONFIRMAR RETO", key=f"btn_{challenge['id']}"):
                                    challenge['completed'] = True
                                    challenge['date_str'] = stats['date'].strftime("%d/%m/%Y")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error("No cumples los requisitos.")

st.divider()

# 4. Footer y Botón de Compartir
share_text = f"🚴‍♂️ *BINGO GURE 2026* 🔴⚫ %0A✅ {completed_count}/16 Retos completados."
group_link = "https://t.me/c/GURE_Ultra/50105"

st.markdown(f"""
    <div style="text-align: center;">
        <p style="font-size: 12px; color: gray; margin-bottom: 5px;">Copia tu resultado y pégalo en el grupo:</p>
        <code style="background: #f1f1f1; padding: 5px; border-radius: 4px; display: block; margin-bottom: 10px;">
            BINGO GURE: {completed_count}/16 Retos ✅
        </code>
        <a href="{group_link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#229ED9; color:white; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer; display: inline-block;">
                ✈️ IR AL GRUPO TELEGRAM
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><center><small>© 2026 GURE Ultra Team</small></center>", unsafe_allow_html=True)

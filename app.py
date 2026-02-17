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

# --- ESTILOS CSS AVANZADOS (PREMIUM UI) ---
st.markdown("""
    <style>
    /* Importar fuente moderna (opcional, usa sistema por defecto si falla) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* FONDO Y GENERAL */
    .stApp {
        background-color: #f8fafc; /* Gris muy muy claro para el fondo */
        color: #1f2937;
        font-family: 'Inter', sans-serif;
    }
    
    /* CABECERA */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 900 !important;
        font-style: italic;
        text-transform: uppercase;
        letter-spacing: -1px;
        margin-bottom: 0 !important;
        font-size: 2.5rem !important;
    }
    h1 span {
        color: #DC2626;
    }
    .caption-text {
        font-size: 1.1rem;
        color: #64748b;
        font-weight: 500;
        margin-top: -10px;
    }

    /* TARJETAS DE RETO (CARDS) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        overflow: hidden; /* Para que la barra de color no se salga */
        position: relative;
    }
    
    /* Efecto Hover en las tarjetas */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #cbd5e1;
    }

    /* BOTONES */
    .stButton > button {
        background: linear-gradient(135deg, #DC2626 0%, #b91c1c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 0.6rem 1rem;
        width: 100%;
        box-shadow: 0 4px 6px rgba(220, 38, 38, 0.2);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ef4444 0%, #DC2626 100%);
        box-shadow: 0 6px 10px rgba(220, 38, 38, 0.3);
        color: white;
        border: none;
    }

    /* MÉTRICAS (CAJA DESTACADA) */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        color: #DC2626;
        font-size: 2rem !important;
        font-weight: 900;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Barra de Progreso */
    div[data-testid="stProgress"] > div > div > div {
        background-color: #DC2626;
        height: 12px;
        border-radius: 10px;
    }

    /* UPLOAD FILE */
    div[data-testid="stFileUploader"] {
        padding-top: 10px;
    }
    div[data-testid="stFileUploader"] section {
        background-color: #f8fafc;
        border: 1px dashed #cbd5e1;
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-testid="stFileUploader"] button {
        background-color: white;
        color: #475569;
        border: 1px solid #cbd5e1;
    }

    /* EXPANDE (Validar) */
    .streamlit-expanderHeader {
        background-color: transparent;
        color: #4b5563;
        font-size: 0.9rem;
        border: none;
        padding-left: 0;
    }
    .streamlit-expanderContent {
        border-top: 1px solid #f1f5f9;
        padding-top: 10px;
    }
    
    /* ICONOS GRANDES EN TARJETAS */
    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: block;
        text-align: center;
    }
    .card-title {
        font-weight: 800;
        font-size: 1rem;
        color: #111827;
        text-align: center;
        margin-bottom: 5px;
        line-height: 1.2;
    }
    .card-desc {
        font-size: 0.8rem;
        color: #64748b;
        text-align: center;
        line-height: 1.4;
        min-height: 2.8em;
        margin-bottom: 10px;
    }
    
    /* ETIQUETAS DE ESTADO */
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 5px;
        width: 100%;
        text-align: center;
    }
    .status-pending {
        background-color: #f1f5f9;
        color: #64748b;
    }
    .status-done {
        background-color: #dcfce7;
        color: #166534;
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
    time.sleep(0.7) 
    seed = sum(ord(c) for c in uploaded_file.name)
    random.seed(seed)
    
    duration = random.randint(30, 240) 
    calories = duration * random.randint(8, 16) 
    intensity_factor = round(random.uniform(0.6, 1.2), 2) 
    max_gradient = random.randint(4, 18) 
    
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
    
    if stats['date'].year == 2026 and stats['date'].month == 3:
        logs.append("✅ Fecha correcta")
    else:
        logs.append("⚠️ Fecha incorrecta (Demo)")
        
    if "minDuration" in rules:
        if stats['duration'] >= rules['minDuration']: logs.append(f"✅ Duración OK ({stats['duration']}m)")
        else:
            logs.append(f"❌ Muy corto ({stats['duration']}m)")
            is_valid = False
            
    if "maxDuration" in rules:
        if stats['duration'] <= rules['maxDuration']: logs.append(f"✅ Tiempo OK ({stats['duration']}m)")
        else:
            logs.append(f"❌ Muy largo ({stats['duration']}m)")
            is_valid = False

    if "minCalories" in rules:
        if stats['calories'] >= rules['minCalories']: logs.append(f"✅ Kcal OK ({stats['calories']})")
        else:
            logs.append(f"❌ Pocas Kcal ({stats['calories']})")
            is_valid = False
            
    if "minIF" in rules:
        if stats['if'] >= rules['minIF']: logs.append(f"✅ IF OK ({stats['if']})")
        else:
            logs.append(f"❌ Falta gas (IF {stats['if']})")
            is_valid = False
            
    if "minGradient" in rules:
        if stats['gradient'] >= rules['minGradient']: logs.append(f"✅ Rampa OK ({stats['gradient']}%)")
        else:
            logs.append(f"❌ Muy suave ({stats['gradient']}%)")
            is_valid = False
            
    if "maxTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str < rules['maxTime']: logs.append(f"✅ Hora OK ({time_str})")
        else:
             logs.append(f"❌ Tarde ({time_str})")
             is_valid = False

    if "minTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str > rules['minTime']: logs.append(f"✅ Hora OK ({time_str})")
        else:
             logs.append(f"❌ Pronto ({time_str})")
             is_valid = False
             
    return is_valid, logs

# --- INTERFAZ UI ---

# 1. Cabecera Limpia
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://gureultra.com/wp-content/uploads/2024/10/GureUltra.png", use_container_width=True)
with col_title:
    st.markdown("<h1>BINGO CICLISTA <span>GURE</span></h1>", unsafe_allow_html=True)
    st.markdown('<p class="caption-text">Un reto para la más Ciclópatas</p>', unsafe_allow_html=True)

st.markdown("---")

# 2. Panel de Progreso Destacado
completed_count = sum(1 for c in st.session_state.challenges if c['completed'])
cols_metrics = st.columns([3, 1, 1])
with cols_metrics[0]:
    st.caption("PROGRESO GLOBAL")
    st.progress(completed_count / 16)
with cols_metrics[1]:
    st.metric("RETOS", f"{completed_count}/16")
with cols_metrics[2]:
    st.metric("ESTADO", "🔥" if completed_count > 0 else "💤")

st.markdown("<br>", unsafe_allow_html=True)

# 3. Grid de Tarjetas (Diseño Visual)
rows = [st.session_state.challenges[i:i + 4] for i in range(0, 16, 4)]

for row in rows:
    cols = st.columns(4)
    for idx, challenge in enumerate(row):
        with cols[idx]:
            # Contenedor con borde = Tarjeta
            with st.container(border=True):
                # Estado visual
                if challenge['completed']:
                    st.markdown(f"<div class='status-badge status-done'>COMPLETADO</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='status-badge status-pending'>PENDIENTE</div>", unsafe_allow_html=True)
                
                # Icono y Título grandes
                st.markdown(f"<div class='card-icon'>{challenge['icon']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-title'>{challenge['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-desc'>{challenge['desc']}</div>", unsafe_allow_html=True)
                
                # Lógica de Botones
                if challenge['completed']:
                    st.caption(f"📅 {challenge.get('date_str', 'Hecho')}")
                    if st.button("↺", key=f"undo_{challenge['id']}", help="Deshacer reto"):
                        challenge['completed'] = False
                        st.rerun()
                else:
                    # Expander limpio para validar
                    with st.expander("Subir .FIT"):
                        uploaded_file = st.file_uploader("", type=['fit'], key=f"up_{challenge['id']}", label_visibility="collapsed")
                        
                        if uploaded_file:
                            with st.spinner('Validando...'):
                                stats = parse_fit_file_simulated(uploaded_file)
                                is_valid, logs = validate_rules(stats, challenge['rules'])
                                
                                st.markdown(f"**{stats['duration']}min** | **{stats['calories']}kcal**")
                                
                                # Mostrar solo errores si falla, o check si ok
                                if not is_valid:
                                    for log in logs:
                                        if "❌" in log: st.caption(f":red[{log}]")
                                    st.error("No válido")
                                else:
                                    st.success("¡Válido!")
                                    if st.button("CONFIRMAR", key=f"btn_{challenge['id']}"):
                                        challenge['completed'] = True
                                        challenge['date_str'] = stats['date'].strftime("%d/%m")
                                        st.balloons()
                                        time.sleep(0.5)
                                        st.rerun()

st.markdown("---")

# 4. Botón de Acción Final (Rojo GURE)
group_link = "https://t.me/c/GURE_Ultra/50105"

st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <a href="{group_link}" target="_blank" style="text-decoration:none;">
            <div style="
                background: linear-gradient(135deg, #DC2626 0%, #991b1b 100%);
                color: white;
                padding: 16px 32px;
                border-radius: 50px;
                font-weight: 800;
                font-size: 18px;
                letter-spacing: 1px;
                box-shadow: 0 10px 20px -5px rgba(220, 38, 38, 0.4);
                display: inline-block;
                transition: transform 0.2s;
            ">
                🚀 COMPARTE TU AVANCE DEL RETO
            </div>
        </a>
        <p style="margin-top: 15px; font-size: 12px; color: #94a3b8;">
            Llevas {completed_count} de 16 retos completados
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><center><small style='color: #cbd5e1;'>© 2026 GURE Ultra Team</small></center>", unsafe_allow_html=True)

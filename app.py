import streamlit as st
import datetime
import random
import time
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Bingo Ciclista Gure",
    page_icon="🚴",
    layout="centered"
)

# Intentar importar fitparse.
try:
    import fitparse
except ImportError:
    st.error("🚨 Falta la librería 'fitparse'. Añádela a tu requirements.txt")
    st.stop()

# --- CONEXIÓN A GOOGLE SHEETS (CON EL TRUCO DEL JSON STRING) ---
@st.cache_resource
def init_connection():
    try:
        scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Leemos el JSON en crudo desde los secrets
        json_str = st.secrets["gcp_service_account_json"]
        creds_dict = json.loads(json_str)
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scopes)
        client = gspread.authorize(creds)
        # Asegúrate de que tu hoja se llame exactamente "BingoGureDB"
        sheet = client.open("BingoGureDB").sheet1 
        return sheet
    except Exception as e:
        # Modo local/demo si falla la conexión
        st.sidebar.warning(f"⚠️ Modo Local (Error BBDD: {e})")
        return None

sheet = init_connection()

# --- FUNCIONES DE BASE DE DATOS ---
def load_user_progress(username):
    if sheet is None: return []
    try:
        records = sheet.get_all_records()
        user_records = [r for r in records if str(r['Usuario']).lower() == username.lower()]
        return [r['Reto_ID'] for r in user_records]
    except:
        return []

def save_challenge_completion(username, challenge_id, date_str, evidence="FIT Validado"):
    if sheet is None: return
    try:
        # Añadir fila: Usuario, Reto_ID, Fecha, Evidencia
        sheet.append_row([username, challenge_id, date_str, evidence])
    except Exception as e:
        st.error(f"Error al guardar en base de datos: {e}")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Saira:ital,wght@0,400;0,600;0,800;0,900;1,900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    .stApp { background-color: #f8fafc; color: #1f2937; font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Saira', sans-serif !important; font-weight: 900 !important; font-style: italic; text-transform: uppercase; letter-spacing: -0.02em; margin-bottom: 0 !important; font-size: 3rem !important; line-height: 1 !important; }
    h1 span { color: #DC2626; }
    .caption-text { font-family: 'Saira', sans-serif; font-size: 1.2rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-top: 5px; letter-spacing: 0.5px; }

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); transition: all 0.3s ease; overflow: hidden; position: relative;
    }
    
    .stButton > button { background: linear-gradient(135deg, #DC2626 0%, #b91c1c 100%); color: white; border: none; border-radius: 8px; font-family: 'Saira', sans-serif; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 0.6rem 1rem; width: 100%; box-shadow: 0 4px 6px rgba(220, 38, 38, 0.2); }
    .stButton > button:hover { background: linear-gradient(135deg, #ef4444 0%, #DC2626 100%); color: white; border: none; }

    div[data-testid="metric-container"] { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #f1f5f9; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: center; }
    div[data-testid="stMetricValue"] { font-family: 'Saira', sans-serif; color: #DC2626; font-size: 2.2rem !important; font-weight: 900; line-height: 1; }
    div[data-testid="stMetricLabel"] { font-family: 'Saira', sans-serif; font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; }

    div[data-testid="stProgress"] > div > div > div { background-color: #DC2626; height: 12px; border-radius: 10px; }
    
    .card-icon { font-size: 2.5rem; margin-bottom: 0.5rem; display: block; text-align: center; }
    .card-title { font-family: 'Saira', sans-serif; font-weight: 800; font-size: 1.1rem; color: #111827; text-transform: uppercase; text-align: center; margin-bottom: 5px; line-height: 1.1; }
    .card-desc { font-size: 0.85rem; color: #64748b; text-align: center; line-height: 1.4; min-height: 2.8em; margin-bottom: 10px; }
    
    .status-badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-family: 'Saira', sans-serif; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; width: 100%; text-align: center; }
    .status-pending { background-color: #f1f5f9; color: #94a3b8; }
    .status-done { background-color: #000000; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# --- DEFINICIÓN DE RETOS BASE ---
BASE_CHALLENGES = [
    {"id": 1, "title": "El Panadero", "desc": "Terminar antes de las 08:00 AM", "icon": "☀️", "type": "fit", "rules": {"maxTime": "08:00"}},
    {"id": 2, "title": "El Vampiro", "desc": "Empezar después de las 21:00 PM", "icon": "🌙", "type": "fit", "rules": {"minTime": "21:00"}},
    {"id": 3, "title": "Doblete Finde", "desc": "Entrenar Sábado y Domingo", "icon": "📅", "type": "fit", "rules": {"mustBeWeekend": True}},
    {"id": 4, "title": "El Expreso", "desc": "< 45 min a IF ≥ 1.0", "icon": "⚡", "type": "fit", "rules": {"maxDuration": 45, "minIF": 1.0}},
    {"id": 5, "title": "Viva Galicia", "desc": "Ruta por tierras gallegas", "icon": "🗺️", "type": "fit", "rules": {"requiredRegion": "Galicia"}},
    {"id": 6, "title": "Ruta Bkool", "desc": "Completar ruta Bkool en Rouvy", "icon": "📺", "type": "fit", "rules": {"requiredDevice": ["bkool", "rouvy"]}},
    {"id": 7, "title": "La Clásica", "desc": "Tramo mítico o Monumento", "icon": "🏆", "type": "fit", "rules": {"isClassic": True}},
    {"id": 8, "title": "El Exótico", "desc": "Ruta en continente distinto", "icon": "🌍", "type": "fit", "rules": {"isExotic": True}},
    {"id": 9, "title": "El Molinillo", "desc": "Cadencia media > 85 rpm", "icon": "🔄", "type": "fit", "rules": {"minCadence": 85}},
    {"id": 10, "title": "Zona Confort", "desc": ">1h sin pasar de Zona 2", "icon": "❤️", "type": "fit", "rules": {"minDuration": 60, "maxHRZone": 2}},
    {"id": 11, "title": "El Muro", "desc": "Rampa del 14% o superior", "icon": "⛰️", "type": "fit", "rules": {"minGradient": 14}},
    {"id": 12, "title": "Capicúa", "desc": "Distancia capicúa (ej: 22.22km)", "icon": "#️⃣", "type": "fit", "rules": {"isPalindrome": True}},
    {"id": 13, "title": "Coffee Ride", "desc": "Foto con café/cerveza", "icon": "☕", "type": "image", "rules": {}},
    {"id": 14, "title": "Grupeta", "desc": "Coincidir con alguien", "icon": "👥", "type": "fit", "rules": {"minParticipants": 2}},
    {"id": 15, "title": "Gran Fondo", "desc": "Sesión > 3h seguidas", "icon": "📈", "type": "fit", "rules": {"minDuration": 180}},
    {"id": 16, "title": "Los Torreznos", "desc": "Quemar > 1.500 kcal", "icon": "🔥", "type": "fit", "rules": {"minCalories": 1500}},
]

# --- LÓGICA DE LOGIN ---
if 'username' not in st.session_state:
    st.session_state.username = None

if st.session_state.username is None:
    col_logo, _ = st.columns([1, 2])
    st.image("https://gureultra.com/wp-content/uploads/2024/10/GureUltra.png", width=200)
    st.markdown("<h1>BINGO CICLISTA <span>GURE</span></h1>", unsafe_allow_html=True)
    st.markdown("### Identifícate para guardar tu progreso")
    
    with st.form("login_form"):
        username_input = st.text_input("Nombre de usuario (Telegram o Alias)", placeholder="Ej: globero_99")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button and username_input:
            st.session_state.username = username_input
            # Cargar estado guardado de este usuario
            completed_ids = load_user_progress(username_input)
            
            # Inicializar los retos con el estado del usuario
            st.session_state.challenges = []
            for base_c in BASE_CHALLENGES:
                c_copy = base_c.copy()
                c_copy["completed"] = c_copy["id"] in completed_ids
                st.session_state.challenges.append(c_copy)
            
            st.rerun()
    st.stop()

# --- USUARIO LOGUEADO: CABECERA ---
col_logo, col_title = st.columns([1, 3])
with col_logo:
    st.image("https://gureultra.com/wp-content/uploads/2024/10/GureUltra.png", use_container_width=True)
with col_title:
    st.markdown("<h1>BINGO CICLISTA <span>GURE</span></h1>", unsafe_allow_html=True)
    st.markdown('<p class="caption-text">Un reto para los más ciclópatas</p>', unsafe_allow_html=True)
    
    # Botón para cerrar sesión o cambiar de usuario
    st.caption(f"👤 Ciclópata: **{st.session_state.username}**")
    if st.button("Cambiar usuario", size="small"):
        st.session_state.username = None
        st.rerun()

st.markdown("---")

completed_count = sum(1 for c in st.session_state.challenges if c['completed'])
cols_metrics = st.columns([3, 1, 1])
with cols_metrics[0]:
    st.caption("PROGRESO GLOBAL")
    st.progress(completed_count / 16)
with cols_metrics[1]:
    st.metric("RETOS", f"{completed_count}/16")
with cols_metrics[2]:
    st.metric("ESTADO", "🔥" if completed_count > 0 else "💤")

with st.expander("ℹ️ Instrucciones de uso"):
    st.markdown("""
    **¿Cómo jugar?**
    1. Despliega una casilla del bingo que quieras intentar.
    2. Sube el archivo `.FIT` real de tu dispositivo (Garmin, Wahoo, Coros, etc.) o simulador.
    3. Para el reto *Coffee Ride*, sube la foto en JPG/PNG.
    4. El sistema evaluará los metadatos de tu archivo. ¡Tus avances se guardan automáticamente!
    """)

st.markdown("<br>", unsafe_allow_html=True)

# --- EXTRACTOR DE DATOS FIT REAL (Usando fitparse) ---
def parse_fit_file_real(uploaded_file):
    try:
        fitfile = fitparse.FitFile(uploaded_file.read())
        stats = {
            "date": None, "duration": 0, "calories": 0, "if": 0.0, "gradient": 0, "cadence": 0,
            "max_hr_zone": 5, "distance": 0.0, "region": "Desconocida", "device": "Desconocido",
            "is_classic": False, "is_exotic": False
        }
        for record in fitfile.get_messages('file_id'):
            for data in record:
                if data.name == 'manufacturer': stats["device"] = str(data.value).lower()
        
        for record in fitfile.get_messages('session'):
            for data in record:
                if data.name == 'start_time' and data.value: stats["date"] = data.value
                elif data.name == 'total_elapsed_time' and data.value: stats["duration"] = data.value / 60.0
                elif data.name == 'total_calories' and data.value: stats["calories"] = data.value
                elif data.name == 'intensity_factor' and data.value: stats["if"] = data.value
                elif data.name == 'avg_cadence' and data.value: stats["cadence"] = data.value
                elif data.name == 'total_distance' and data.value: stats["distance"] = data.value / 1000.0
                elif data.name == 'avg_heart_rate' and data.value:
                    if data.value <= 135: stats["max_hr_zone"] = 2
                    elif data.value <= 155: stats["max_hr_zone"] = 3
                    else: stats["max_hr_zone"] = 4
                            
        if not stats["date"]: stats["date"] = datetime.datetime.now()
        return stats
    except Exception as e:
        return None

# --- MOTOR DE REGLAS EXHAUSTIVO ---
def validate_rules(stats, rules):
    logs = []
    is_valid = True
    
    if stats['date'].year == 2026 and stats['date'].month == 3: logs.append("✅ Reto realizado en Marzo 2026")
    else:
        logs.append("❌ El archivo no es de Marzo de 2026")
        is_valid = False
        
    if "maxTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str < rules['maxTime']: logs.append(f"✅ Terminaste antes de las {rules['maxTime']} ({time_str})")
        else: logs.append(f"❌ Terminaste tarde ({time_str})"); is_valid = False

    if "minTime" in rules:
        time_str = stats['date'].strftime("%H:%M")
        if time_str > rules['minTime']: logs.append(f"✅ Empezaste después de las {rules['minTime']} ({time_str})")
        else: logs.append(f"❌ Empezaste muy pronto ({time_str})"); is_valid = False

    if "mustBeWeekend" in rules:
        if stats['date'].weekday() >= 5: logs.append(f"✅ Realizado en fin de semana")
        else: logs.append(f"❌ Realizado entre semana"); is_valid = False

    if "minDuration" in rules:
        if stats['duration'] >= rules['minDuration']: logs.append(f"✅ Duración OK ({stats['duration']:.0f} min)")
        else: logs.append(f"❌ Muy corto ({stats['duration']:.0f} min)"); is_valid = False
            
    if "maxDuration" in rules:
        if stats['duration'] <= rules['maxDuration']: logs.append(f"✅ Tiempo OK ({stats['duration']:.0f} min)")
        else: logs.append(f"❌ Te pasaste de tiempo ({stats['duration']:.0f} min)"); is_valid = False

    if "minCalories" in rules:
        if stats['calories'] >= rules['minCalories']: logs.append(f"✅ Kcal OK ({stats['calories']} kcal)")
        else: logs.append(f"❌ Pocas Kcal ({stats['calories']} kcal)"); is_valid = False
            
    if "minIF" in rules:
        if stats['if'] >= rules['minIF']: logs.append(f"✅ IF OK ({stats['if']})")
        elif stats['if'] == 0.0: logs.append(f"⚠️ Sin datos de IF en archivo. Válido bajo honor.")
        else: logs.append(f"❌ Falta gas (IF {stats['if']})"); is_valid = False

    if "minCadence" in rules:
        if stats['cadence'] >= rules['minCadence']: logs.append(f"✅ Molinillo OK ({stats['cadence']} rpm)")
        elif stats['cadence'] == 0: logs.append(f"⚠️ Sin sensor de cadencia. Válido bajo honor.")
        else: logs.append(f"❌ Atrancado ({stats['cadence']} rpm)"); is_valid = False

    if "isPalindrome" in rules:
        dist_str = f"{stats['distance']:.2f}"
        dist_clean = dist_str.replace('.', '')
        if dist_clean == dist_clean[::-1]: logs.append(f"✅ Capicúa ({dist_str} km)")
        else: logs.append(f"❌ No es capicúa ({dist_str} km)"); is_valid = False
             
    return is_valid, logs

# --- RENDERIZADO DEL GRID ---
rows = [st.session_state.challenges[i:i + 4] for i in range(0, 16, 4)]

for row in rows:
    cols = st.columns(4)
    for idx, challenge in enumerate(row):
        with cols[idx]:
            with st.container(border=True):
                if challenge['completed']:
                    st.markdown(f"<div class='status-badge status-done'>COMPLETADO</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='status-badge status-pending'>PENDIENTE</div>", unsafe_allow_html=True)
                
                st.markdown(f"<div class='card-icon'>{challenge['icon']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-title'>{challenge['title']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-desc'>{challenge['desc']}</div>", unsafe_allow_html=True)
                
                if challenge['completed']:
                    st.caption(f"📅 Registrado en la base de datos")
                else:
                    challenge_type = challenge.get('type', 'fit')
                    label_text = "Sube imagen" if challenge_type == 'image' else "Subir .FIT"
                    file_types = ['png', 'jpg', 'jpeg'] if challenge_type == 'image' else ['fit']
                    
                    with st.expander(label_text):
                        uploaded_file = st.file_uploader("", type=file_types, key=f"up_{challenge['id']}", label_visibility="collapsed")
                        
                        if uploaded_file:
                            if challenge_type == 'image':
                                st.image(uploaded_file, caption="Evidencia", use_container_width=True)
                                if st.button("CONFIRMAR FOTO", key=f"btn_{challenge['id']}"):
                                    # GUARDAR EN GOOGLE SHEETS
                                    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                                    save_challenge_completion(st.session_state.username, challenge['id'], date_str, "Foto")
                                    
                                    challenge['completed'] = True
                                    st.balloons()
                                    time.sleep(0.5)
                                    st.rerun()
                            else:
                                with st.spinner('Procesando archivo binario...'):
                                    stats = parse_fit_file_real(uploaded_file)
                                    
                                    if stats is None:
                                        st.error("Error leyendo el archivo FIT. Puede estar corrupto o usar un formato no soportado.")
                                    else:
                                        is_valid, logs = validate_rules(stats, challenge['rules'])
                                        
                                        st.markdown(f"**{stats['distance']:.1f}km** | **{stats['duration']:.0f}min** | **{stats['cadence']}rpm**")
                                        
                                        if not is_valid:
                                            for log in logs:
                                                if "❌" in log: st.caption(f":red[{log}]")
                                            st.error("Archivo no válido para este reto")
                                        else:
                                            for log in logs:
                                                if "✅" in log: st.caption(f":green[{log}]")
                                                elif "⚠️" in log: st.caption(f":orange[{log}]")
                                            st.success("¡Reto conseguido!")
                                            if st.button("GUARDAR LOGRO", key=f"btn_{challenge['id']}"):
                                                # GUARDAR EN GOOGLE SHEETS
                                                date_str = stats['date'].strftime("%Y-%m-%d %H:%M")
                                                save_challenge_completion(st.session_state.username, challenge['id'], date_str, uploaded_file.name)
                                                
                                                challenge['completed'] = True
                                                st.balloons()
                                                time.sleep(0.5)
                                                st.rerun()

st.markdown("---")

# --- BOTÓN DE COMPARTIR AVANZADO ---
group_link = "https://t.me/GURE_ultra_Channel"

completed_list = [c['title'] for c in st.session_state.challenges if c['completed']]
if completed_list:
    challenges_joined = "\\n✅ ".join(completed_list)
    clipboard_content = f"🚴‍♂️ *BINGO GURE 2026* ({st.session_state.username}) 🔴⚫\\n\\n🏆 Progreso: {completed_count}/16\\n\\nHe completado:\\n✅ {challenges_joined}\\n\\n#BingoGure"
else:
    clipboard_content = f"🚴‍♂️ *BINGO GURE 2026* ({st.session_state.username}) 🔴⚫\\n\\n¡Empiezo el reto! 0/16 completados.\\n\\n#BingoGure"

# Reemplazamos las comillas dobles y simples para que la inyección en JS funcione correctamente
clipboard_content_js = clipboard_content.replace('"', '\\"').replace("'", "\\'")

st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <a href="{group_link}" target="_blank" onclick="navigator.clipboard.writeText('{clipboard_content_js}'); alert('¡Resumen copiado! Pégalo en el canal.');" style="text-decoration:none;">
            <div style="background: linear-gradient(135deg, #DC2626 0%, #991b1b 100%); color: white; padding: 16px 32px; border-radius: 50px; font-family: 'Saira', sans-serif; font-weight: 800; font-size: 18px; letter-spacing: 1px; box-shadow: 0 10px 20px -5px rgba(220, 38, 38, 0.4); display: inline-block; transition: transform 0.2s;">
                🚀 COMPARTE TU AVANCE DEL RETO
            </div>
        </a>
    </div>
""", unsafe_allow_html=True)

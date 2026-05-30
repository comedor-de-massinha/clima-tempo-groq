import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# 1. Tenta carregar do .env local (vai funcionar na sua máquina)
load_dotenv()

# 2. Busca a chave primeiro no .env / Sistema e, se não achar, busca no Secrets do Streamlit
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = None

# Inicializa o cliente se encontrar a chave em algum dos dois lugares
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

st.set_page_config(
    page_title="ClimAI",
    page_icon="🌤️",
    layout="wide"
)

# Estilização para mesclar e tornar os campos do formulário invisíveis
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: #0f172a !important;
}
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
iframe {
    border: none !important;
}
/* Remove bordas e margens do container do form do Streamlit */
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
/* Torna os campos de texto da ponte completamente invisíveis na tela */
div[data-testid="stForm"] div[data-testid="stTextInput"] {
    display: none !important;
}
/* Botão de envio do Streamlit responsivo */
div[data-testid="stForm"] .stButton>button,
.stButton>button {
    width: auto !important;
    max-width: 360px !important;
    margin: 0 auto !important;
    display: block !important;
    min-height: 44px !important;
    padding: 0.8rem 1.2rem !important;
}
</style>
""", unsafe_allow_html=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- HTML SEM O BOTÃO CONSULTAR e COM ENVIO RÁPIDO AO CLICAR ---
HTML = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.tailwindcss.com"></script>
<style>
:root{
    --bg:#0f172a;
    --card:#0b1220;
    --muted:#9ca3af;
    --text:#e5e7eb;
    --accent:#3b82f6;
    --input-bg:#071129;
    --border:#213547;
    --btn-bg:#06b6d4;
}
body{
    background:var(--bg);
    color:var(--text);
    font-family:sans-serif;
    margin:0;
    padding:20px 16px 30px;
}
h1 {
    font-size: clamp(32px, 6vw, 44px);
    margin-bottom: 0.4rem;
}
p {
    font-size: clamp(14px, 2vw, 16px);
}
.weather-card{
    background:var(--card);
    border:1px solid #1f2937;
}
.recommendation{
    background:var(--card);
    border-left:5px solid var(--accent);
}
.custom-scrollbar::-webkit-scrollbar{
    width:6px;
}
.custom-scrollbar::-webkit-scrollbar-track{
    background:var(--input-bg);
}
.custom-scrollbar::-webkit-scrollbar-thumb{
    background:#1e293b;
    border-radius:3px;
}
</style>
</head>
<body>
<br><br>

<div class="w-full max-w-2xl mx-auto">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-extrabold">🌤️ ClimAI</h1>
        <p class="text-sm text-gray-400">Inteligência climática</p>
    </div>

    <div class="relative w-full mb-6">
        <input
            id="cidade-input"
            autocomplete="off"
            placeholder="Digite o nome da cidade (ex: São Paulo, Curitiba...)"
            class="w-full px-4 py-3 rounded-lg text-gray-200 outline-none text-base"
            style="background:var(--input-bg); border:1px solid var(--border);"
        >
        <div
            id="js-suggestions"
            class="absolute left-0 right-0 z-50 mt-1 max-h-60 overflow-y-auto rounded-lg hidden custom-scrollbar"
            style="background:var(--input-bg); border:1px solid var(--border);"
        ></div>
    </div>

    <div id="alert-zone" class="hidden mb-4 text-sm px-4 py-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400"></div>

    <div id="resultado-container" class="hidden space-y-4">
        <div class="weather-card p-6 rounded-2xl">
            <h2 id="res-cidade" class="text-2xl font-bold mb-4"></h2>
            <div class="grid gap-3 text-sm">
                <p><b>🌡️ Temperatura:</b> <span id="res-temp"></span>°C</p>
                <p><b>🥵 Sensação térmica:</b> <span id="res-sensacao"></span>°C</p>
                <p><b>💧 Umidade:</b> <span id="res-umidade"></span>%</p>
                <p><b>🌬️ Vento:</b> <span id="res-vento"></span> m/s</p>
                <p><b>☁️ Clima:</b> <span id="res-clima"></span></p>
            </div>
        </div>

        <div class="recommendation p-5 rounded-xl">
            <h3 class="text-cyan-400 mb-2">📦 Raw API Response Body</h3>
            <pre id="res-json" class="text-xs text-gray-300 bg-black/30 p-3 rounded-lg overflow-auto custom-scrollbar"></pre>
        </div>
    </div>
</div>

<script>
const input=document.getElementById("cidade-input");
const suggestions=document.getElementById("js-suggestions");
let timer=null;

const WEATHER_CODE_MAP={
    0:"Céu limpo", 1:"Principalmente limpo", 2:"Parcialmente nublado", 3:"Nublado"
};

input.addEventListener("input",(e)=>{
    const q=e.target.value.trim();
    clearTimeout(timer);
    if(q.length<2){ suggestions.classList.add("hidden"); return; }

    timer=setTimeout(async()=>{
        const resp=await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(q)}&count=8&language=pt`);
        const data=await resp.json();
        suggestions.innerHTML="";
        suggestions.classList.remove("hidden");

        (data.results || []).forEach(item=>{
            const div=document.createElement("div");
            div.className="p-3 text-sm text-gray-300 hover:bg-[#0b2a3a] cursor-pointer";
            div.textContent=`${item.name}${item.admin1 ? ", "+item.admin1 : ""} - ${item.country}`;
            div.onclick=()=>{
                input.value=div.textContent;
                suggestions.classList.add("hidden");
                consultar(item);
            };
            suggestions.appendChild(div);
        });
    },300);
});

async function consultar(cidade){
    const climaResp=await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${cidade.latitude}&longitude=${cidade.longitude}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=auto`);
    const clima=await climaResp.json();
    const current=clima.current;

    document.getElementById("res-cidade").textContent="📍 "+cidade.name;
    document.getElementById("res-temp").textContent=current.temperature_2m;
    document.getElementById("res-sensacao").textContent=current.temperature_2m;
    document.getElementById("res-umidade").textContent=current.relative_humidity_2m;
    document.getElementById("res-vento").textContent=current.wind_speed_10m;
    document.getElementById("res-clima").textContent=WEATHER_CODE_MAP[current.weather_code] || "Condição climática";
    document.getElementById("res-json").textContent=JSON.stringify(clima,null,2);
    document.getElementById("resultado-container").classList.remove("hidden");

    const condicao = WEATHER_CODE_MAP[current.weather_code] || "Desconhecido";
    
    // Captura os inputs invisíveis do Streamlit presentes na página externa
    const stInputs = window.parent.document.querySelectorAll('input[type="text"]');
    
    if(stInputs.length >= 3) {
        const dados = [cidade.name, current.temperature_2m.toString(), condicao];
        
        dados.forEach((valor, index) => {
            const el = stInputs[index];
            // Sincroniza com a árvore interna de estados do React do Streamlit
            const valorNativoSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            valorNativoSetter.call(el, valor);
            el.dispatchEvent(new Event('input', { bubbles: true }));
        });
    }
}
</script>
</body>
</html>
"""

# Renderiza o painel principal do HTML com a caixa de busca em duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.components.v1.html(HTML, height=560, scrolling=True)

with col2:
    st.markdown(
        "<div style='display:flex; flex-direction:column; align-items:center; justify-content:flex-start; gap:16px; padding: 16px 8px;'>"
        "<div style='text-align:center;'>"
        "<br><br><h2 style='margin:0; font-size:1.9rem; color:#ffffff;'>Gerar Insights</h2>"
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("ponte_dados_oculta", clear_on_submit=False):
        cidade_st = st.text_input("C", key="st_cid")
        temp_st = st.text_input("T", key="st_tmp")
        cond_st = st.text_input("O", key="st_cnd")

        st.markdown(
            "<div style='width:100%; display:flex; justify-content:center; padding: 0 8px;'>"
            "<div style='width:100%; max-width:320px;'>",
            unsafe_allow_html=True
        )

        is_cidade_empty = not cidade_st or not cidade_st.strip()
        
        st.markdown(f"""
        <style>
        .disabled-btn-wrapper button {{
            cursor: {'not-allowed' if is_cidade_empty else 'pointer'} !important;
            opacity: {'0.6' if is_cidade_empty else '1'} !important;
        }}
        </style>
        <div class="disabled-btn-wrapper">
        """, unsafe_allow_html=True)

        enviar_groq = st.form_submit_button("Gerar Insights Inteligentes", type="primary")

        st.markdown("</div></div></div>", unsafe_allow_html=True)

    response_slot = st.empty()

# Execução e retorno da IA
if enviar_groq:
    if not cidade_st:
        st.warning("Selecione uma localidade na lista de sugestões acima para liberar os parâmetros de análise.")
    elif not client:
        st.error("Chave 'GROQ_API_KEY' não foi identificada no arquivo .env.")
    else:
        with st.spinner("Solicitando recomendações ao Llama 3.1..."):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Você é o ClimAI. Dê conselhos curtos, práticos e objetivos de saúde, vestuário e atividades ideais para as condições atuais informadas."
                        },
                        {
                            "role": "user",
                            "content": f"Cidade: {cidade_st}. Temperatura: {temp_st}°C. Condição atual: {cond_st}."
                        }
                    ],
                    temperature=0.6,
                    max_tokens=300
                )
                
                resposta = completion.choices[0].message.content
                
                response_slot.markdown(f"""
                <div style="background: #0b1220; border-left: 5px solid #06b6d4; padding: 20px; border-radius: 12px; margin-top: 15px; color: #e5e7eb; font-family: sans-serif; border: 1px solid #1f2937; max-width: 100%;">
                    <h4 style="color: #06b6d4; margin-top: 0; font-weight: bold; margin-bottom: 10px;">🤖 Recomendações ClimAI (Groq)</h4>
                    <div style="font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{resposta}</div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao chamar a API do Groq: {e}")

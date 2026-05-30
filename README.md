# ClimAI 🌤️

Sistema de clima inteligente com Streamlit + Groq.

## Funcionalidades

- Consulta clima em tempo real
- Integração com Open-Meteo (API pública, sem chave)
 - Integração com Open-Meteo (API pública, sem chave)
 - Tema escuro aplicado por padrão (UI adaptada para visual noturno)
- IA da Groq gera recomendações inteligentes
- Interface moderna
- Dropdown de cidades
- TailwindCSS
- Streamlit

## Instalação

### Criar ambiente virtual

```bash
python -m venv venv
```

### Ativar ambiente

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Configurar .env

```env
GROQ_API_KEY=sua_chave

```

## Rodar projeto

```bash
streamlit run app.py
```

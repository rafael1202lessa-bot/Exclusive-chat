import streamlit as st
from supabase import create_client, Client

# Configuração da página do Chat
st.set_page_config(page_title="Chat Privado da Galera", page_icon="💬", layout="centered")

# --- CONEXÃO COM O SEU BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Erro de conexão com o servidor.")

# --- DEFINIÇÃO DA SENHA DE SEGURANÇA ---
SENHA_CORRETA = "galera123" 

# Controle de sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

# --- TELA 1: BARREIRA DE SEGURANÇA ---
if not st.session_state.logado:
    st.title("🔒 Chat Privado")
    st.markdown("Este é um espaço seguro e restrito. Digite suas credenciais para entrar.")
    
    nome = st.text_input("Seu Nome ou Apelido:", placeholder="Ex: Luccas").strip()
    senha_digitada = st.text_input("Senha de Acesso do Grupo:", type="password", placeholder="Digite a senha secreta")
    
    if st.button("Entrar no Chat 🚀"):
        if nome == "" or senha_digitada == "":
            st.error("Por favor, preencha todos os campos!")
        elif senha_digitada != SENHA_CORRETA:
            st.error("Senha incorreta! Acesso negado.")
        else:
            st.session_state.logado = True
            st.session_state.nome_usuario = nome
            st.rerun()

# --- TELA 2: O CHAT DE CONVERSAS ---
else:
    st.title("💬 Chat Oficial da Galera")
    st.write(f"Conectado como: **{st.session_state.nome_usuario}**")
    
    if st.sidebar.button("Sair do Chat 🚪"):
        st.session_state.logado = False
        st.session_state.nome_usuario = ""
        st.rerun()

    with st.container():
        nova_msg = st.text_input("Digite sua mensagem:", placeholder="Escreva aqui...", key="campo_texto")
        if st.button("Enviar Mensagem ✉️"):
            if nova_msg.strip() != "":
                try:
                    supabase.table("chat_geral").insert({
                        "usuario": st.session_state.nome_usuario,
                        "mensagem": nova_msg.strip()
                    }).execute()
                    st.rerun()
                except Exception as e:
                    st.error("Não foi possível enviar a mensagem no momento.")
            else:
                st.warning("Não é possível enviar uma mensagem vazia!")

    st.markdown("---")
    st.subheader("📋 Mensagens Recentes")

    try:
        resposta = supabase.table("chat_geral").select("*").order("criado_em", desc=True).limit(50).execute()
        
        if resposta.data:
            for msg in resposta.data:
                data_hora = msg['criado_em'].split("T")[1][:5] if "T" in msg['criado_em'] else ""
                
                if msg['usuario'] == st.session_state.nome_usuario:
                    st.markdown(f"🔹 **Você** [{data_hora}]: {msg['mensagem']}")
                else:
                    st.markdown(f"👤 **{msg['usuario']}** [{data_hora}]: {msg['mensagem']}")
        else:
            st.write("Nenhuma mensagem por aqui ainda. Comece a conversar!")
            
    except Exception as e:
        st.write("Aguardando conexão correta com o servidor...")
        

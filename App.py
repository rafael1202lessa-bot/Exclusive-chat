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

# Controle de sessão (se está logado ou não)
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
            st.experimental_rerun()

# --- TELA 2: O CHAT DE CONVERSAS ---
else:
    st.title("💬 Chat Oficial da Galera")
    st.write(f"Conectado como: **{st.session_state.nome_usuario}**")
    
    # Botão para deslogar com segurança
    if st.sidebar.button("Sair do Chat 🚪"):
        st.session_state.logado = False
        st.session_state.nome_usuario = ""
        st.experimental_rerun()

    # --- CAMPO PARA ENVIAR MENSAGEM ---
    with st.container():
        nova_msg = st.text_input("Digite sua mensagem:", placeholder="Escreva aqui...", key="campo_texto")
        if st.button("Enviar Mensagem ✉️"):
            if nova_msg.strip() != "":
                try:
                    # Tentativa 1: Nome padrão das colunas
                    supabase.table("chat_geral").insert({
                        "usuario": st.session_state.nome_usuario,
                        "mensagem": nova_msg.strip()
                    }).execute()
                    st.experimental_rerun()
                except Exception as e:
                    try:
                        # Tentativa 2: Caso o tradutor do navegador tenha criado como 'usuario text'
                        supabase.table("chat_geral").insert({
                            "usuario text": st.session_state.nome_usuario,
                            "mensagem": nova_msg.strip()
                        }).execute()
                        st.experimental_rerun()
                    except Exception as e2:
                        try:
                            # Tentativa 3: Caso tenha mudado mensagem para 'mensagem text' também
                            supabase.table("chat_geral").insert({
                                "usuario text": st.session_state.nome_usuario,
                                "mensagem text": nova_msg.strip()
                            }).execute()
                            st.experimental_rerun()
                        except Exception as e3:
                            st.error("Erro na estrutura da tabela do Supabase. Verifique os nomes das colunas.")
            else:
                st.warning("Não é possível enviar uma mensagem vazia!")

    st.markdown("---")
    st.subheader("📋 Mensagens Recentes")

    # --- ÁREA DE EXIBIÇÃO DAS MENSAGENS ---
    try:
        resposta = supabase.table("chat_geral").select("*").order("criado_em", desc=True).limit(50).execute()
        
        if resposta.data:
            for msg in resposta.data:
                # Adaptação para ler 'criado_em' gerado pela tradução
                data_hora = msg['criado_em'].split("T")[1][:5] if 'criado_em' in msg and "T" in msg['criado_em'] else ""
                
                if msg.get('usuario') == st.session_state.nome_usuario or msg.get('usuario text') == st.session_state.nome_usuario:
                    texto_msg = msg.get('mensagem') or msg.get('mensagem text') or ""
                    st.markdown(f"🔹 **Você** [{data_hora}]: {texto_msg}")
                else:
                    usuario_nome = msg.get('usuario') or msg.get('usuario text') or "Usuário"
                    texto_msg = msg.get('mensagem') or msg.get('mensagem text') or ""
                    st.markdown(f"👤 **{usuario_nome}** [{data_hora}]: {texto_msg}")
        else:
            st.write("Nenhuma mensagem por aqui ainda. Comece a conversar!")
            
    except Exception as e:
        st.write("Aguardando novas mensagens...")
        

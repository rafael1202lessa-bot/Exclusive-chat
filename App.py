import streamlit as st
from supabase import create_client, Client

# 1. Configuração da página do Streamlit
st.set_page_config(page_title="Chat EXV", page_icon="💬", layout="centered")

# 2. Conexão direta com o seu Supabase
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def iniciar_banco():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

banco = iniciar_banco()

# 3. Gerenciar as variáveis de estado do login
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario_id = ""

# =========================================================
# TELA DE LOGIN / CADASTRO (SINCRONIZADA COM O PRINT)
# =========================================================
if not st.session_state.logado:
    st.title("💬 Chat EXV — Entrar no Universo")
    
    aba_login, aba_cadastro = st.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        user_login = st.text_input("Nome de Usuário", key="user_log", placeholder="Ex: Rafael_oficial").strip()
        senha_login = st.text_input("Senha", type="password", key="senha_log")
        
        if st.button("Entrar", key="btn_log"):
            if not user_login or not senha_login:
                st.warning("Preencha o usuário e a senha!")
            else:
                try:
                    # Busca usando o nome exato da coluna: "nome de usuário"
                    resposta = banco.table("perfis_usuarios").select("*").eq("nome de usuário", user_login).execute()
                    dados_usuario = resposta.data
                    
                    if len(dados_usuario) > 0 and str(dados_usuario[0].get("senha")) == str(senha_login):
                        st.session_state.logado = True
                        st.session_state.usuario_id = user_login
                        st.success(f"Bem-vindo de volta, {user_login}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")
                except Exception as e:
                    st.error(f"Erro ao fazer login: {e}")
                
    with aba_cadastro:
        user_cad = st.text_input("Crie um Nome de Usuário único", key="user_cad", placeholder="Ex: Rafael_oficial").strip()
        senha_cad = st.text_input("Crie sua Senha", type="password", key="senha_cad")
        
        if st.button("Criar Minha Conta", key="btn_cad"):
            if not user_cad or not senha_cad:
                st.warning("Por favor, preencha todos os campos!")
            else:
                try:
                    # Checa se o usuário já existe na coluna correta
                    checar = banco.table("perfis_usuarios").select("*").eq("nome de usuário", user_cad).execute()
                    if len(checar.data) > 0:
                        st.error("Este Nome de Usuário já está sendo usado!")
                    else:
                        # Monta o dicionário com os nomes exatos das colunas do seu print
                        dados_salvar = {
                            "nome de usuário": user_cad,
                            "senha": senha_cad
                        }
                        
                        banco.table("perfis_usuarios").insert(dados_salvar).execute()
                        st.success(f"Conta @{user_cad} criada com sucesso! Já pode entrar.")
                except Exception as e:
                    st.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP (SÓ APARECE APÓS O LOGIN)
# =========================================================
else:
    st.sidebar.title("👤 Seu Perfil EXV")
    st.sidebar.write(f"Conectado como: `@{st.session_state.usuario_id}`")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("💬 Universo Chat EXV")
    
    aba_chat_grupo, aba_chat_privado, aba_amigos, aba_ligacao = st.tabs([
        "👥 Chat em Grupo", "🔒 Conversa Privada", "🤝 Adicionar Amigos", "📞 Ligação EXV"
    ])
    
    with aba_chat_grupo:
        st.subheader("🌐 Sala Global")
        st.write(f"Olá @{st.session_state.usuario_id}, bem-vindo ao grupo!")
        

import streamlit as str
from supabase import create_client, Client

# 1. Configuração da página do Streamlit
str.set_page_config(page_title="Chat EXV", page_icon="💬", layout="centered")

# 2. Conexão direta com o seu Supabase
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

# Inicializa o cliente do banco de dados de forma segura no Streamlit
@str.cache_resource
def iniciar_banco():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

banco = iniciar_banco()

# 3. Gerenciar o estado do login (saber se o usuário já entrou ou não)
if "logado" not in str.session_state:
    str.session_state.logado = False
    str.session_state.usuario_email = ""

# =========================================================
# TELA DE LOGIN / CADASTRO
# =========================================================
if not str.session_state.logado:
    str.title("💬 Chat EXV — Entrar no Universo")
    
    # Abas para organizar entre Entrar e Criar Conta
    aba_login, aba_cadastro = str.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        email_login = str.text_input("E-mail", key="email_log")
        senha_login = str.text_input("Senha", type="password", key="senha_log")
        
        if str.button("Entrar", key="btn_log"):
            try:
                # Tenta fazer o login no Supabase
                resposta = banco.auth.sign_in_with_password({"email": email_login, "password": senha_login})
                str.session_state.logado = True
                str.session_state.usuario_email = email_login
                str.success("Bem-vindo ao Chat EXV!")
                str.rerun() # Atualiza a tela para mostrar o chat
            except Exception as e:
                str.error(f"Erro ao entrar: {e}")
                
    with aba_cadastro:
        email_cad = str.text_input("E-mail", key="email_cad")
        senha_cad = str.text_input("Senha (mínimo 6 caracteres)", type="password", key="senha_cad")
        
        if str.button("Criar Minha Conta", key="btn_cad"):
            if len(senha_cad) < 6:
                str.warning("A senha precisa ter pelo menos 6 caracteres!")
            else:
                try:
                    # Tenta criar a conta no Supabase
                    resposta = banco.auth.sign_up({"email": email_cad, "password": senha_cad})
                    str.success("Conta criada com sucesso! Agora vá na aba 'Entrar'.")
                except Exception as e:
                    str.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP (SÓ APARECE APÓS O LOGIN)
# =========================================================
else:
    # Barra lateral com informações do usuário e botão de sair
    str.sidebar.title("👤 Seu Perfil")
    str.sidebar.write(f"Conectado como:\n**{str.session_state.usuario_email}**")
    
    if str.sidebar.button("🚪 Sair do Chat"):
        banco.auth.sign_out()
        str.session_state.logado = False
        str.session_state.usuario_email = ""
        str.rerun()

    # Corpo principal do Chat EXV
    str.title("🚀 Chat EXV — Painel Principal")
    str.write("Você está conectado! O sistema de autenticação está funcionando.")
    
    # [Aqui vamos programar as salas de chat, áudio e fotos nos próximos passos!]
    str.info("Próximo passo: Criar a tabela de mensagens no Supabase para liberar o chat de texto.")
    

import streamlit as str
from supabase import create_client, Client

# 1. Configuração da página do Streamlit
str.set_page_config(page_title="Chat EXV", page_icon="💬", layout="centered")

# 2. Conexão direta com o seu Supabase
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@str.cache_resource
def iniciar_banco():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

banco = iniciar_banco()

# 3. Gerenciar as variáveis de estado do login
if "logado" not in str.session_state:
    str.session_state.logado = False
    str.session_state.usuario_id = ""
    str.session_state.usuario_nome = "Usuário"
    str.session_state.usuario_foto = ""

# =========================================================
# TELA DE LOGIN / CADASTRO (SEM GMAIL)
# =========================================================
if not str.session_state.logado:
    str.title("💬 Chat EXV — Entrar no Universo")
    
    aba_login, aba_cadastro = str.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        user_login = str.text_input("Nome de Usuário", key="user_log", placeholder="Ex: rafael123").strip().lower()
        senha_login = str.text_input("Senha", type="password", key="senha_log")
        
        if str.button("Entrar", key="btn_log"):
            if not user_login or not senha_login:
                str.warning("Preencha o usuário e a senha!")
            else:
                try:
                    # Transforma o nome de usuário no formato que o Supabase exige internamente
                    email_interno = f"{user_login}@chatexv.com"
                    
                    # Fazer login no Supabase
                    resposta = banco.auth.sign_in_with_password({"email": email_interno, "password": senha_login})
                    
                    # Pegar os dados do perfil salvos
                    metadados = resposta.user.user_metadata
                    
                    str.session_state.logado = True
                    str.session_state.usuario_id = user_login
                    str.session_state.usuario_nome = metadados.get("nome", user_login)
                    str.session_state.usuario_foto = metadados.get("foto_url", "")
                    
                    str.success(f"Bem-vindo de volta, {str.session_state.usuario_nome}!")
                    str.rerun()
                except Exception as e:
                    str.error("Usuário ou senha incorretos!")
                
    with aba_cadastro:
        user_cad = str.text_input("Crie um Nome de Usuário único", key="user_cad", placeholder="Ex: rafael123 (Não use espaços)").strip().lower()
        nome_exibicao = str.text_input("Nome de Exibição (Como os amigos vão te ver)", key="nome_exib", placeholder="Ex: Rafael Lessa")
        senha_cad = str.text_input("Senha (mínimo 6 caracteres)", type="password", key="senha_cad")
        
        # Campo para fazer upload da foto de perfil direto do celular
        foto_perfil = str.file_uploader("Escolha sua foto de perfil", type=["png", "jpg", "jpeg"])
        
        if str.button("Criar Minha Conta", key="btn_cad"):
            if not user_cad or not nome_exibicao or not list(user_cad):
                str.warning("Por favor, preencha todos os campos de texto!")
            elif " " in user_cad:
                str.warning("O Nome de Usuário não pode conter espaços vazios!")
            elif len(senha_cad) < 6:
                str.warning("A senha precisa ter pelo menos 6 caracteres!")
            else:
                try:
                    foto_url = ""
                    email_interno = f"{user_cad}@chatexv.com"
                    
                    # Se escolheu uma foto, envia para o Storage
                    if foto_perfil is not None:
                        bytes_foto = foto_perfil.getvalue()
                        nome_arquivo = f"avatar_{user_cad}.png"
                        
                        # Envia o arquivo para o bucket 'avatares'
                        banco.storage.from_("avatares").upload(
                            path=nome_arquivo,
                            file=bytes_foto,
                            file_options={"content-type": "image/png"}
                        )
                        
                        # Pega o link público da foto enviada
                        foto_url = banco.storage.from_("avatares").get_public_url(nome_arquivo)
                    
                    # Cria a conta usando o email mascarado e salva os dados reais nos metadados
                    resposta = banco.auth.sign_up({
                        "email": email_interno, 
                        "password": senha_cad,
                        "options": {
                            "data": {
                                "nome": nome_exibicao,
                                "foto_url": foto_url
                            }
                        }
                    })
                    
                    str.success(f"Conta @{user_cad} criada com sucesso! Agora vá na aba 'Entrar'.")
                except Exception as e:
                    str.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP (SÓ APARECE APÓS O LOGIN)
# =========================================================
else:
    # Barra lateral estilizada com a foto e o nome do usuário
    str.sidebar.title("👤 Seu Perfil EXV")
    
    if str.session_state.usuario_foto:
        str.sidebar.image(str.session_state.usuario_foto, width=100)
        
    str.sidebar.write(f"Nome: **{str.session_state.usuario_nome}**")
    str.sidebar.write(f"ID: `@{str.session_state.usuario_id}`")
    
    if str.sidebar.button("🚪 Sair"):
        banco.auth.sign_out()
        str.session_state.logado = False
        str.session_state.usuario_id = ""
        str.session_state.usuario_nome = "Usuário"
        str.session_state.usuario_foto = ""
        str.rerun()

    # Painel Principal do Chat EXV
    str.title(f"🚀 Chat EXV — Olá, {str.session_state.usuario_nome}!")
    str.write("Sistema de contas limpo, sem e-mails e totalmente configurado.")
    
    str.success("Próximo passo: Criar a área de mensagens de texto!")
    

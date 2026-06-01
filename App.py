import streamlit as str
from supabase import create_client, Client
import mimetypes

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
    str.session_state.usuario_email = ""
    str.session_state.usuario_nome = "Usuário"
    str.session_state.usuario_foto = ""

# =========================================================
# TELA DE LOGIN / CADASTRO
# =========================================================
if not str.session_state.logado:
    str.title("💬 Chat EXV — Cadastro e Acesso")
    
    aba_login, aba_cadastro = str.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        email_login = str.text_input("E-mail", key="email_log")
        senha_login = str.text_input("Senha", type="password", key="senha_log")
        
        if str.button("Entrar", key="btn_log"):
            try:
                # Fazer login no Supabase
                resposta = banco.auth.sign_in_with_password({"email": email_login, "password": senha_login})
                
                # Buscar o nome e a foto que foram salvos nos metadados do usuário
                metadados = resposta.user.user_metadata
                
                str.session_state.logado = True
                str.session_state.usuario_email = email_login
                str.session_state.usuario_nome = metadados.get("nome", "Usuário")
                str.session_state.usuario_foto = metadados.get("foto_url", "")
                
                str.success(f"Bem-vindo de volta, {str.session_state.usuario_nome}!")
                str.rerun()
            except Exception as e:
                str.error(f"Erro ao entrar: {e}")
                
    with aba_cadastro:
        nome_cad = str.text_input("Seu Nome / Apelido", key="nome_cad")
        email_cad = str.text_input("E-mail", key="email_cad")
        senha_cad = str.text_input("Senha (mínimo 6 caracteres)", type="password", key="senha_cad")
        
        # Campo para fazer upload da foto de perfil direto do celular
        foto_perfil = str.file_uploader("Escolha sua foto de perfil", type=["png", "jpg", "jpeg"])
        
        if str.button("Criar Minha Conta", key="btn_cad"):
            if not nome_cad:
                str.warning("Por favor, digite o seu nome!")
            elif len(senha_cad) < 6:
                str.warning("A senha precisa ter pelo menos 6 caracteres!")
            else:
                try:
                    foto_url = ""
                    
                    # Se o usuário escolheu uma foto, vamos subir para o Storage do Supabase
                    if foto_perfil is not None:
                        bytes_foto = foto_perfil.getvalue()
                        nome_arquivo = f"avatar_{email_cad.replace('@', '_').replace('.', '_')}.png"
                        
                        # Envia o arquivo para o bucket 'avatares'
                        banco.storage.from_("avatares").upload(
                            path=nome_arquivo,
                            file=bytes_foto,
                            file_options={"content-type": "image/png"}
                        )
                        
                        # Pega o link público da foto enviada
                        foto_url = banco.storage.from_("avatares").get_public_url(nome_arquivo)
                    
                    # Cria a conta no Supabase salvando o Nome e a URL da foto junto
                    resposta = banco.auth.sign_up({
                        "email": email_cad, 
                        "password": senha_cad,
                        "options": {
                            "data": {
                                "nome": nome_cad,
                                "foto_url": foto_url
                            }
                        }
                    })
                    
                    str.success("Conta criada com sucesso com foto e nome! Agora vá na aba 'Entrar'.")
                except Exception as e:
                    str.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP (SÓ APARECE APÓS O LOGIN)
# =========================================================
else:
    # Barra lateral estilizada com a foto e o nome do usuário
    str.sidebar.title("👤 Seu Perfil")
    
    # Se o usuário tiver foto, exibe ela redondinha na barra lateral
    if str.session_state.usuario_foto:
        str.sidebar.image(str.session_state.usuario_foto, width=100)
        
    str.sidebar.write(f"Nome: **{str.session_state.usuario_nome}**")
    str.sidebar.write(f"E-mail: *{str.session_state.usuario_email}*")
    
    if str.sidebar.button("🚪 Sair do Chat"):
        banco.auth.sign_out()
        str.session_state.logado = False
        str.session_state.usuario_email = ""
        str.session_state.usuario_nome = "Usuário"
        str.session_state.usuario_foto = ""
        str.rerun()

    # Painel Principal do Chat EXV
    str.title(f"🚀 Chat EXV — Olá, {str.session_state.usuario_nome}!")
    str.write("O seu perfil está totalmente configurado e autenticado no banco de dados.")
    
    # Confirmação visual de que deu certo
    str.success("Próximo passo: Criar o layout de mensagens privadas e em grupo!")
    

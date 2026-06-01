import streamlit as st
from supabase import create_client, Client

# 1. Configuração da página do Streamlit
st.set_page_config(page_title="Chat EXV", page_icon="💬", layout="centered")

# 2. Conexão direta com o teu Supabase
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
    st.session_state.usuario_nome = "Usuário"
    st.session_state.usuario_foto = ""

# =========================================================
# TELA DE LOGIN / CADASTRO (SISTEMA PRÓPRIO SEM E-MAIL)
# =========================================================
if not st.session_state.logado:
    st.title("💬 Chat EXV — Entrar no Universo")
    
    aba_login, aba_cadastro = st.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        user_login = st.text_input("Nome de Usuário", key="user_log", placeholder="Ex: rafael123").strip().lower()
        senha_login = st.text_input("Senha", type="password", key="senha_log")
        
        if st.button("Entrar", key="btn_log"):
            if not user_login or not senha_login:
                st.warning("Preencha o usuário e a senha!")
            else:
                try:
                    # Procura o usuário diretamente na nossa tabela
                    resposta = banco.table("usuarios").select("*").eq("usuario_id", user_login).execute()
                    dados_usuario = resposta.data
                    
                    if len(dados_usuario) > 0 and dados_usuario[0]["senha"] == senha_login:
                        st.session_state.logado = True
                        st.session_state.usuario_id = user_login
                        st.session_state.usuario_nome = dados_usuario[0]["nome"]
                        st.session_state.usuario_foto = dados_usuario[0]["foto_url"]
                        
                        st.success(f"Bem-vindo de volta, {st.session_state.usuario_nome}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")
                except Exception as e:
                    st.error(f"Erro ao fazer login: {e}")
                
    with aba_cadastro:
        user_cad = st.text_input("Crie um Nome de Usuário único", key="user_cad", placeholder="Ex: rafael123").strip().lower()
        nome_exibicao = st.text_input("Nome de Exibição", key="nome_exib", placeholder="Ex: Rafael")
        senha_cad = st.text_input("Senha", type="password", key="senha_cad")
        foto_perfil = st.file_uploader("Escolha sua foto de perfil", type=["png", "jpg", "jpeg"])
        
        if st.button("Criar Minha Conta", key="btn_cad"):
            if not user_cad or not nome_exibicao or not senha_cad:
                st.warning("Por favor, preencha todos os campos!")
            elif " " in user_cad:
                st.warning("O Nome de Usuário não can conter espaços!")
            else:
                try:
                    # Verifica se o ID já existe para não duplicar
                    checar = banco.table("usuarios").select("*").eq("usuario_id", user_cad).execute()
                    if len(checar.data) > 0:
                        st.error("Este Nome de Usuário já está a ser usado por outra pessoa!")
                    else:
                        foto_url = ""
                        # Se escolheu uma foto, envia para o Storage
                        if foto_perfil is not None:
                            bytes_foto = foto_perfil.getvalue()
                            nome_arquivo = f"avatar_{user_cad}.png"
                            
                            # Envia para o bucket
                            banco.storage.from_("avatares").upload(
                                path=nome_arquivo,
                                file=bytes_foto,
                                file_options={"content-type": "image/png"}
                            )
                            foto_url = banco.storage.from_("avatares").get_public_url(nome_arquivo)
                        
                        # Insere o novo usuário na tabela do banco de dados
                        banco.table("usuarios").insert({
                            "usuario_id": user_cad,
                            "nome": nome_exibicao,
                            "senha": senha_cad,
                            "foto_url": foto_url
                        }).execute()
                        
                        st.success(f"Conta @{user_cad} criada com sucesso! Já podes entrar.")
                except Exception as e:
                    st.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP (SÓ APARECE APÓS O LOGIN)
# =========================================================
else:
    st.sidebar.title("👤 Seu Perfil EXV")
    if st.session_state.usuario_foto:
        st.sidebar.image(st.session_state.usuario_foto, width=100)
    st.sidebar.write(f"Nome: **{st.session_state.usuario_nome}**")
    st.sidebar.write(f"ID: `@{st.session_state.usuario_id}`")
    
    if st.sidebar.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("💬 Universo Chat EXV")
    
    aba_chat_grupo, aba_chat_privado, aba_amigos, aba_ligacao = st.tabs([
        "👥 Chat em Grupo", "🔒 Conversa Privada", "🤝 Adicionar Amigos", "📞 Ligação EXV"
    ])
    
    with aba_chat_grupo:
        st.subheader("🌐 Sala Global")
        st.write("*Pronto para começar a enviar mensagens sem bloqueios!*")
        

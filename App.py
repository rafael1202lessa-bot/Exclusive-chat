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
# TELA DE LOGIN / CADASTRO
# =========================================================
if not st.session_state.logado:
    st.title("💬 Chat EXV — Entrar no Universo")
    
    aba_login, aba_cadastro = st.tabs(["🔓 Entrar", "✨ Criar Conta"])
    
    with aba_login:
        user_login = st.text_input("Nome de Usuário (Nick)", key="user_log", placeholder="Ex: rafael_oficial").strip().lower()
        senha_login = st.text_input("Senha", type="password", key="senha_log")
        
        if st.button("Entrar", key="btn_log"):
            if not user_login or not senha_login:
                st.warning("Preencha o usuário e a senha!")
            else:
                try:
                    resposta = banco.table("perfis_exv").select("*").eq("usuario_id", user_login).execute()
                    dados_usuario = resposta.data
                    
                    if len(dados_usuario) > 0 and str(dados_usuario[0].get("senha")) == str(senha_login):
                        st.session_state.logado = True
                        st.session_state.usuario_id = user_login
                        st.session_state.usuario_nome = dados_usuario[0].get("nome_exibicao", user_login)
                        st.session_state.usuario_foto = dados_usuario[0].get("foto_url", "")
                        
                        st.success(f"Bem-vindo de volta, {st.session_state.usuario_nome}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos!")
                except Exception as e:
                    st.error(f"Erro ao fazer login: {e}")
                
    with aba_cadastro:
        user_cad = st.text_input("Crie um Nome de Usuário único (Nick)", key="user_cad", placeholder="Ex: rafael_oficial").strip().lower()
        nome_exib_cad = st.text_input("Nome de Exibição (Como os amigos vão te ver)", key="nome_exib", placeholder="Ex: Rafael Lessa")
        senha_cad = st.text_input("Crie sua Senha", type="password", key="senha_cad")
        foto_perfil = st.file_uploader("Escolha sua foto de perfil", type=["png", "jpg", "jpeg"])
        
        if st.button("Criar Minha Conta", key="btn_cad"):
            if not user_cad or not nome_exib_cad or not senha_cad:
                st.warning("Por favor, preencha todos os campos!")
            elif " " in user_cad:
                st.warning("O Nome de Usuário (Nick) não pode conter espaços!")
            else:
                try:
                    checar = banco.table("perfis_exv").select("*").eq("usuario_id", user_cad).execute()
                    if len(checar.data) > 0:
                        st.error("Este Nome de Usuário já está sendo usado!")
                    else:
                        foto_url = ""
                        if foto_perfil is not None:
                            try:
                                bytes_foto = foto_perfil.getvalue()
                                nome_arquivo = f"avatar_{user_cad}.png"
                                
                                banco.storage.from_("avatares").upload(
                                    path=nome_arquivo,
                                    file=bytes_foto,
                                    file_options={"content-type": "image/png"}
                                )
                                foto_url = banco.storage.from_("avatares").get_public_url(nome_arquivo)
                            except Exception:
                                foto_url = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                        
                        dados_salvar = {
                            "usuario_id": user_cad,
                            "nome_exibicao": nome_exib_cad,
                            "senha": senha_cad,
                            "foto_url": foto_url
                        }
                        
                        banco.table("perfis_exv").insert(dados_salvar).execute()
                        st.success(f"Conta @{user_cad} criada com sucesso! Já pode entrar na aba correspondente.")
                except Exception as e:
                    st.error(f"Erro no cadastro: {e}")

# =========================================================
# TELA DO APP COM ABAS
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
    
    # --- ABA 1: CHAT EM GRUPO ---
    with aba_chat_grupo:
        st.subheader("🌐 Sala Global do Chat EXV")
        
        try:
            resp_msgs = banco.table("mensagens_grupo").select("*").order("created_at", desc=False).execute()
            lista_mensagens = resp_msgs.data
        except Exception:
            lista_mensagens = []
            
        chat_container = st.container()
        with chat_container:
            if lista_mensagens:
                for m in lista_mensagens:
                    remetente = m.get("usuario_id", "Desconhecido")
                    texto_msg = m.get("texto", "")
                    nome_exib = m.get("nome_exibicao", remetente)
                    
                    if remetente == st.session_state.usuario_id:
                        st.markdown(f"💬 **Você ({nome_exib}):** {texto_msg}")
                    else:
                        st.markdown(f"💬 **{nome_exib}:** {texto_msg}")
            else:
                st.info("Nenhuma mensagem na sala global ainda. Mande a primeira!")

        with st.form(key="form_envio_grupo", clear_on_submit=True):
            msg_grupo = st.text_input("Escreva sua mensagem para o grupo...", placeholder="Digite aqui...")
            btn_enviar_grupo = st.form_submit_button("Enviar Mensagem 🚀")
            
            if btn_enviar_grupo and msg_grupo.strip():
                try:
                    banco.table("mensagens_grupo").insert({
                        "usuario_id": st.session_state.usuario_id,
                        "nome_exibicao": st.session_state.usuario_nome,
                        "texto": msg_grupo.strip()
                    }).execute()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao enviar mensagem: {e}")

    # --- ABA 2: CONVERSA PRIVADA ---
    with aba_chat_privado:
        st.subheader("🔒 Mensagens Privadas (Direct)")
        
        try:
            # Pega todos os usuários cadastrados para você escolher com quem falar (exceto você mesmo)
            resp_perfis = banco.table("perfis_exv").select("usuario_id, nome_exibicao").neq("usuario_id", st.session_state.usuario_id).execute()
            outros_usuarios = resp_perfis.data
        except Exception:
            outros_usuarios = []
            
        if not outros_usuarios:
            st.info("Ainda não há outros usuários cadastrados para conversar em privado. Crie outra conta para testar!")
        else:
            # Cria um dicionário para mapear Nome de Exibição -> usuario_id
            opcoes_amigos = {f"{u['nome_exibicao']} (@{u['usuario_id']})": u['usuario_id'] for u in outros_usuarios}
            
            amigo_escolhido_label = st.selectbox("Escolha com quem quer conversar:", list(opcoes_amigos.keys()))
            destinatario_id = opcoes_amigos[amigo_escolhido_label]
            
            st.markdown("---")
            
            # Buscar mensagens privadas entre VOCÊ e o DESTINATÁRIO
            try:
                # Buscamos mensagens onde (remetente = eu E destinatario = ele) OU (remetente = ele E destinatario = eu)
                resp_pv = banco.table("mensagens_privadas").select("*").or_(
                    f"and(remetente_id.eq.{st.session_state.usuario_id},destinatario_id.eq.{destinatario_id}),and(remetente_id.eq.{destinatario_id},destinatario_id.eq.{st.session_state.usuario_id})"
                ).order("created_at", desc=False).execute()
                mensagens_pv = resp_pv.data
            except Exception:
                mensagens_pv = []
                
            # Exibe o histórico do chat privado
            priv_container = st.container()
            with priv_container:
                if mensagens_pv:
                    for mp in mensagens_pv:
                        rem = mp.get("remetente_id")
                        txt = mp.get("texto")
                        if rem == st.session_state.usuario_id:
                            st.markdown(f"🔒 **Você:** {txt}")
                        else:
                            st.markdown(f"🔒 **{amigo_escolhido_label.split(' ')[0]}:** {txt}")
                else:
                    st.info(f"Nenhuma mensagem privada com {amigo_escolhido_label.split(' ')[0]} ainda. Mande a primeira!")
            
            # Caixa de envio da mensagem privada
            with st.form(key="form_envio_privado", clear_on_submit=True):
                msg_privada = st.text_input("Escreva sua mensagem secreta...", placeholder="Digite aqui...")
                btn_enviar_priv = st.form_submit_button("Enviar Privado 🔒")
                
                if btn_enviar_priv and msg_privada.strip():
                    try:
                        banco.table("mensagens_privadas").insert({
                            "remetente_id": st.session_state.usuario_id,
                            "destinatario_id": destinatario_id,
                            "texto": msg_privada.strip()
                        }).execute()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao enviar mensagem privada: {e}")

    # --- ABA 3: ADICIONAR AMIGOS ---
    with aba_amigos:
        st.subheader("🤝 Seus Amigos")
        st.write("Em breve: adicione amigos pelo ID para criar sua lista de contatos!")

    # --- ABA 4: LIGAÇÃO EXV ---
    with aba_ligacao:
        st.subheader("📞 Ligação EXV")
        st.write("Em breve: chamadas de vídeo e voz no app!")
                

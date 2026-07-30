import streamlit as st
from supabase import create_client, Client
from audio_recorder_streamlit import audio_recorder

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
                        st.success(f"Conta @{user_cad} criada com sucesso! Já pode entrar.")
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
    
    aba_chat_grupo, aba_chat_privado, aba_amigos, aba_audios = st.tabs([
        "👥 Chat em Grupo", "🔒 Conversa Privada", "🤝 Adicionar Amigos", "🎙️ Recados de Voz"
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
                st.info("Nenhuma mensagem na sala global ainda.")

        with st.form(key="form_envio_grupo", clear_on_submit=True):
            msg_grupo = st.text_input("Escreva sua mensagem...", placeholder="Digite aqui...")
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
                    st.error(f"Erro ao enviar: {e}")

    # --- ABA 2: CONVERSA PRIVADA ---
    with aba_chat_privado:
        st.subheader("🔒 Mensagens Privadas (Direct)")
        
        try:
            resp_amigos_aceitos = banco.table("amigos_exv").select("*").eq("status", "aceito").or_(
                f"usuario_id.eq.{st.session_state.usuario_id},amigo_id.eq.{st.session_state.usuario_id}"
            ).execute()
            
            amigos_ids = []
            for rel in resp_amigos_aceitos.data:
                if rel["usuario_id"] == st.session_state.usuario_id:
                    amigos_ids.append(rel["amigo_id"])
                else:
                    amigos_ids.append(rel["usuario_id"])
                    
            meus_amigos_detalhes = []
            if amigos_ids:
                resp_detalhes = banco.table("perfis_exv").select("usuario_id, nome_exibicao").in_("usuario_id", amigos_ids).execute()
                meus_amigos_detalhes = resp_detalhes.data
        except Exception:
            meus_amigos_detalhes = []
            
        if not meus_amigos_detalhes:
            st.info("Você precisa ter amigos aceitos para conversar no privado.")
        else:
            opcoes_amigos = {f"{u['nome_exibicao']} (@{u['usuario_id']})": u['usuario_id'] for u in meus_amigos_detalhes}
            amigo_escolhido_label = st.selectbox("Escolha um amigo:", list(opcoes_amigos.keys()))
            destinatario_id = opcoes_amigos[amigo_escolhido_label]
            
            st.markdown("---")
            
            try:
                resp_pv = banco.table("mensagens_privadas").select("*").or_(
                    f"and(remetente_id.eq.{st.session_state.usuario_id},destinatario_id.eq.{destinatario_id}),and(remetente_id.eq.{destinatario_id},destinatario_id.eq.{st.session_state.usuario_id})"
                ).order("created_at", desc=False).execute()
                mensagens_pv = resp_pv.data
            except Exception:
                mensagens_pv = []
                
            priv_container = st.container()
            with priv_container:
                if mensagens_pv:
                    for mp in mensagens_pv:
                        rem = mp.get("remetente_id")
                        txt = mp.get("texto")
                        if rem == st.session_state.usuario_id:
                            st.markdown(f"🔒 **Você:** {txt}")
                        else:
                            st.markdown(f"🔒 **Amigo:** {txt}")
                else:
                    st.info("Nenhuma mensagem privada ainda.")
            
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
                        st.error(f"Erro: {e}")

    # --- ABA 3: ADICIONAR AMIGOS ---
    with aba_amigos:
        st.subheader("🤝 Gerenciar Amigos")
        
        with st.form(key="form_adicionar_amigo", clear_on_submit=True):
            nick_busca = st.text_input("Enviar pedido de amizade para (Nick):", placeholder="Ex: joao123").strip().lower()
            btn_add = st.form_submit_button("Enviar Pedido ➕")
            
            if btn_add:
                if not nick_busca:
                    st.warning("Digite um Nick válido!")
                elif nick_busca == st.session_state.usuario_id:
                    st.warning("Você não pode adicionar a si mesmo!")
                else:
                    try:
                        busca_usuario = banco.table("perfis_exv").select("*").eq("usuario_id", nick_busca).execute()
                        
                        if len(busca_usuario.data) == 0:
                            st.error("Usuário não encontrado!")
                        else:
                            ja_existe = banco.table("amigos_exv").select("*").or_(
                                f"and(usuario_id.eq.{st.session_state.usuario_id},amigo_id.eq.{nick_busca}),and(usuario_id.eq.{nick_busca},amigo_id.eq.{st.session_state.usuario_id})"
                            ).execute()
                            
                            if len(ja_existe.data) > 0:
                                st.warning("Já existe um pedido ou vocês já são amigos!")
                            else:
                                banco.table("amigos_exv").insert({
                                    "usuario_id": st.session_state.usuario_id,
                                    "amigo_id": nick_busca,
                                    "status": "pendente"
                                }).execute()
                                st.success(f"Pedido enviado para @{nick_busca}!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                        
        st.markdown("---")
        st.subheader("📥 Pedidos Recebidos")
        try:
            resp_pedidos = banco.table("amigos_exv").select("*").eq("amigo_id", st.session_state.usuario_id).eq("status", "pendente").execute()
            pedidos_recebidos = resp_pedidos.data
            
            if pedidos_recebidos:
                for p in pedidos_recebidos:
                    quem_mandou = p["usuario_id"]
                    col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                    with col_p1:
                        st.write(f"@{quem_mandou} quer ser seu amigo.")
                    with col_p2:
                        if st.button("Aceitar ✅", key=f"aceitar_{quem_mandou}"):
                            banco.table("amigos_exv").update({"status": "aceito"}).eq("id", p["id"]).execute()
                            st.rerun()
                    with col_p3:
                        if st.button("Recusar ❌", key=f"recusar_{quem_mandou}"):
                            banco.table("amigos_exv").delete().eq("id", p["id"]).execute()
                            st.rerun()
            else:
                st.info("Nenhum pedido pendente.")
        except Exception:
            pass

    # --- ABA 4: RECADOS DE VOZ (ÁUDIO NO CELULAR) ---
    with aba_audios:
        st.subheader("🎙️ Gravar Recado de Voz (Walkie-Talkie)")
        st.markdown("Toque no botão do microfone abaixo para gravar sua voz direto pelo celular e ouça os recados enviados:")
        
        # Widget para gravar áudio direto no navegador mobile
        audio_bytes = audio_recorder(
            text="Toque para Gravar",
            recording_color="#e74c3c",
            neutral_color="#3498db",
            icon_size="2x"
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.success("Áudio gravado com sucesso! (Você pode ouvi-lo acima antes de enviar)")
            
            if st.button("Enviar Áudio para o Chat Global 🚀"):
                try:
                    # Converte o áudio em bytes para base64 ou salva no Supabase Storage se preferir,
                    # ou reproduz temporariamente.
                    st.info("Áudio capturado! Para salvar permanentemente para todos ouvirem, você pode armazenar no Supabase Storage na tabela de áudios.")
                except Exception as e:
                    st.error(f"Erro ao enviar áudio: {e}")
    

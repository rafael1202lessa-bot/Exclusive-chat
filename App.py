import streamlit as st
from supabase import create_client, Client
import uuid

# Configuração da página
st.set_page_config(page_title="Silver Tok v2.0", page_icon="🎬", layout="centered")

# --- CONEXÃO COM O BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        return None

supabase = init_connection()
if supabase is None:
    st.error("Erro de conexão com o servidor.")
    st.stop()

# --- CONFIGURAÇÕES GERAIS ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "id_upload_chat" not in st.session_state:
    st.session_state.id_upload_chat = str(uuid.uuid4())
if "id_upload_video" not in st.session_state:
    st.session_state.id_upload_video = str(uuid.uuid4())

def apagar_mensagem(id_mensagem):
    try:
        supabase.table("bate-papo_profissional").delete().eq("id", id_mensagem).execute()
        st.toast("Mensagem apagada! 🗑️")
    except:
        st.error("Erro ao deletar.")

# --- TELA DE AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    st.title("🎬 Silver Tok & Chat 🔐")
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    
    with aba_auth[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                try:
                    busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                    if busca.data and busca.data[0]["senha"] == login_senha:
                        st.session_state.usuario_logado = busca.data[0]
                        st.success("Login realizado!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception as e:
                    st.error("Erro ao conectar ao banco de dados.")
            else:
                st.warning("Preencha todos os campos!")

    with aba_auth[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha um Nome de Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        cad_foto = st.file_uploader("Escolha sua Foto de Perfil:", type=["png", "jpg", "jpeg"], key="cad_foto")
        codigo_convite = st.text_input("🔑 Código de Convite Secreto:", type="password", key="codigo_convite")
        
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha:
                if codigo_convite != CHAVE_SECRETA:
                    st.error("❌ Código de Convite incorreto!")
                else:
                    try:
                        url_foto = FOTO_PADRAO
                        if cad_foto:
                            extensao = cad_foto.name.split(".")[-1]
                            nome_arquivo = f"perfis/{uuid.uuid4()}.{extensao}"
                            supabase.storage.from_("imagens_chat").upload(nome_arquivo, cad_foto.read())
                            url_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_arquivo)
                        
                        supabase.table("perfis_usuarios").insert({
                            "username": cad_user,
                            "senha": cad_senha,
                            "url_foto_perfil": url_foto
                        }).execute()
                        st.success("Conta criada! Faça o login na primeira aba.")
                    except:
                        st.error("Usuário já existe ou erro no cadastro.")
            else:
                st.warning("Usuário e senha são obrigatórios!")

# --- APLICATIVO LOGADO ---
else:
    user_atual = st.session_state.usuario_logado
    
    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=90)
    st.sidebar.write(f"Logado como: **{user_atual['username']}**")
    if st.sidebar.button("Sair da Conta 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.rerun()

    aba_principal, aba_batepapo = st.tabs(["📺 Silver Tok (Feed)", "💬 Chat-Exv"])

    # ==================== ABA 1: FEED DE VÍDEOS ====================
    with aba_principal:
        st.title("📺 Silver Tok Feed")
        with st.expander("➕ Publicar Novo Post / Edit"):
            titulo_video = st.text_input("Legenda do Vídeo:", placeholder="Ex: Edit de Bleach! 🔥")
            arquivo_video = st.file_uploader("Selecione o Vídeo (MP4):", type=["mp4"], key=st.session_state.id_upload_video)
            
            if st.button("Publicar Vídeo 🚀", use_container_width=True):
                if arquivo_video and titulo_video.strip() != "":
                    try:
                        ext = arquivo_video.name.split(".")[-1]
                        nome_video_db = f"videos/{uuid.uuid4()}.{ext}"
                        supabase.storage.from_("videos_feed").upload(nome_video_db, arquivo_video.read())
                        url_video_final = supabase.storage.from_("videos_feed").get_public_url(nome_video_db)
                        
                        supabase.table("feed_videos").insert({
                            "titulo": titulo_video.strip(),
                            "url_video": url_video_final,
                            "username_autor": user_atual["username"],
                            "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0
                        }).execute()
                        st.success("Vídeo postado!")
                        st.session_state.id_upload_video = str(uuid.uuid4())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao publicar: {e}")
                else:
                    st.warning("Preencha todos os campos!")

        st.markdown("---")
        try:
            dados_feed = supabase.table("feed_videos").select("*").execute()
            if dados_feed.data:
                for video in reversed(dados_feed.data):
                    col_autor_img, col_autor_txt = st.columns([1, 6])
                    with col_autor_img:
                        st.image(video.get("avatar_autor") or FOTO_PADRAO, width=40)
                    with col_autor_txt:
                        st.markdown(f"**{video.get('username_autor', 'Membro')}**")
                    st.caption(f"{video['titulo']}")
                    st.video(video["url_video"])
                    
                    likes = video.get("curtidas", 0)
                    if st.button(f"❤️ {likes} Curtidas", key=f"like_{video['id']}"):
                        supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", video["id"]).execute()
                        st.rerun()
                    st.markdown("---")
            else:
                st.info("Nenhum vídeo publicado ainda.")
        except:
            st.error("Erro ao carregar o feed.")

    # ==================== ABA 2: CHAT EXCLUSIVO ====================
    with aba_batepapo:
        if st.session_state.sala_ativa is not None:
            st.title(f"💬 Sala Ativa")
            st.code(f"Código: {st.session_state.sala_ativa}")
            if st.button("⬅️ Voltar para o Menu do Chat", use_container_width=True):
                st.session_state.sala_ativa = None
                st.rerun()
            st.markdown("---")

            with st.container():
                txt_msg = st.text_input("Digite sua mensagem:", key="txt_msg_input")
                upload_img = st.file_uploader("Enviar uma Imagem (Opcional):", type=["png", "jpg", "jpeg", "gif"], key=st.session_state.id_upload_chat)
                
                if st.button("Enviar Mensagem ✉️", use_container_width=True):
                    if txt_msg.strip() != "" or upload_img is not None:
                        try:
                            url_img_enviada = None
                            if upload_img:
                                extensao = upload_img.name.split(".")[-1]
                                nome_arquivo = f"chat/{uuid.uuid4()}.{extensao}"
                                supabase.storage.from_("imagens_chat").upload(nome_arquivo, upload_img.read())
                                url_img_enviada = supabase.storage.from_("imagens_chat").get_public_url(nome_arquivo)
                            
                            supabase.table("bate-papo_profissional").insert({
                                "id_usuario": user_atual["id"],
                                "username": user_atual["username"],
                                "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                                "mensagem": txt_msg.strip() if txt_msg.strip() else None,
                                "url_imagem_enviada": url_img_enviada,
                                "codigo_sala": st.session_state.sala_ativa
                            }).execute()
                            st.session_state.id_upload_chat = str(uuid.uuid4())
                            st.rerun()
                        except:
                            st.error("Erro ao enviar.")
                    else:
                        st.warning("Escreva uma mensagem ou selecione uma imagem!")

            st.markdown("---")
            try:
                resposta = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if resposta.data:
                    for msg in reversed(resposta.data[-40:]):
                        col1, col2, col3 = st.columns([1, 5, 1])
                        with col1:
                            st.image(msg.get("url_foto_perfil") or FOTO_PADRAO, width=45)
                        with col2:
                            st.markdown(f"**{msg['username']}**")
                            if msg.get("mensagem"):
                                st.write(msg["mensagem"])
                            if msg.get("url_imagem_enviada"):
                                st.image(msg["url_imagem_enviada"], use_container_width=True)
                        with col3:
                            if str(msg.get("id_usuario")) == str(user_atual["id"]):
                                if st.button("🗑️", key=f"del_{msg['id']}"):
                                    apagar_mensagem(msg['id'])
                                    st.rerun()
                        st.markdown("---")
                else:
                    st.write("Nenhuma mensagem por aqui.")
            except:
                st.write("Erro ao carregar mensagens.")

        else:
            st.title("🎛️ Painel Chat-Exv")
            menu = st.tabs(["💬 Conversa Privada", "👨‍👩‍👦 Criar Grupo", "🔑 Entrar com Código", "👥 Amigos", "➕ Adicionar"])
            
            with menu[0]:
                st.subheader("Iniciar Chat Particular")
                try:
                    amigos = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    lista_nomes = []
                    mapa_ids = {}
                    for amg in amigos.data:
                        outro_id = amg["id_usuario_recebe"] if str(amg["id_usuario_envio"]) == str(user_atual["id"]) else amg["id_usuario_envio"]
                        dados_user = supabase.table("perfis_usuarios").select("username").eq("id", outro_id).execute()
                        if dados_user.data:
                            nome = dados_user.data[0]["username"]
                            lista_nomes.append(nome)
                            mapa_ids[nome] = outro_id
                    if lista_nomes:
                        alvo = st.selectbox("Selecione o amigo:", lista_nomes)
                        if st.button("Abrir Conversa Particular 🚀", use_container_width=True):
                            ids_ordenados = sorted([str(user_atual["id"]), str(mapa_ids[alvo])])
                            cod_sala_unica = f"PRIVADO-{ids_ordenados[0][:8]}-{ids_ordenados[1][:8]}"
                            st.session_state.sala_ativa = cod_sala_unica
                            st.rerun()
                    else:
                        st.info("Nenhum amigo aceito encontrado.")
                except:
                    st.write("Erro ao carregar amigos.")

            with menu[1]:
                st.subheader("Criar Novo Grupo")
                nome_novo_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Resenha")
                if st.button("Criar Grupo 🎉", use_container_width=True):
                    if nome_novo_grupo:
                        novo_codigo = f"GRUPO-{str(uuid.uuid4())[:8].upper()}"
                        try:
                            supabase.table("salas_chat").insert({"codigo_sala": novo_codigo, "nome_sala": nome_novo_grupo, "tipo": "grupo"}).execute()
                            st.success(f"Criado! Código: **{novo_codigo}**")
                        except:
                            st.error("Erro ao criar grupo.")
                    else:
                        st.warning("Insira um nome!")

            with menu[2]:
                st.subheader("Entrar com Código")
                codigo_digitado = st.text_input("Insira o Código:", placeholder="Ex: GRUPO-XXXX").strip().upper()
                if st.button("Entrar na Sala 🚪", use_container_width=True):
                    if codigo_digitado:
                        st.session_state.sala_ativa = codigo_digitado
                        st.rerun()
                    else:
                        st.warning("Insira um código.")

            with menu[3]:
                st.subheader("Seus Amigos")
                try:
                    pedidos = supabase.table("lista_amigos").select("*").eq("id_usuario_recebe", user_atual["id"]).eq("status", "pendente").execute()
                    if pedidos.data:
                        st.write("📥 **Solicitações:**")
                        for ped in pedidos.data:
                            dados_remetente = supabase.table("perfis_usuarios").select("username").eq("id", ped["id_usuario_envio"]).execute()
                            if dados_remetente.data:
                                col_n, col_a = st.columns([3, 1])
                                with col_n:
                                    st.write(f"De: **{dados_remetente.data[0]['username']}**")
                                with col_a:
                                    if st.button("Aceitar", key=f"ac_{ped['id']}"):
                                        supabase.table("lista_amigos").update({"status": "aceito"}).eq("id", ped["id"]).execute()
                                        st.rerun()
                    
                    confirmados = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    if confirmados.data:
                        st.write("👥 **Amigos:**")
                        for amg in confirmados.data:
                            outro_id = amg["id_usuario_recebe"] if str(amg["id_usuario_envio"]) == str(user_atual["id"]) else amg["id_usuario_envio"]
                            dados_u = supabase.table("perfis_usuarios").select("username").eq("id", outro_id).execute()
                            if dados_u.data:
                                st.write(f"🟢 {dados_u.data[0]['username']}")
                    else:
                        st.caption("Nenhum amigo adicionado.")
                except:
                    st.caption("Erro ao carregar lista.")

            with menu[4]:
                st.subheader("Adicionar Amigo")
                buscar_amigo = st.text_input("Nome do Usuário:", placeholder="Ex: Carlos123").strip()
                if st.button("Enviar Pedido ➕", use_container_width=True):
                    if buscar_amigo:
                        try:
                            alvo_user = supabase.table("perfis_usuarios").select("*").eq("username", buscar_amigo).execute()
                            if alvo_user.data:
                                id_alvo = alvo_user.data[0]["id"]
                                if str(id_alvo) == str(user_atual["id"]):
                                    st.error("Não pode adicionar a si mesmo!")
                                else:
                                    supabase.table("lista_amigos").insert({"id_usuario_envio": user_atual["id"], "id_usuario_recebe": id_alvo, "status": "pendente"}).execute()
                                    st.success(f"Pedido enviado para {buscar_amigo}!")
                            else:
                                st.error("Usuário não encontrado!")
                        except:
                            st.error("Erro ao processar.")
                    else:
                        st.warning("Digite um nome!")
        

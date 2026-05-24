import streamlit as st
from supabase import create_client, Client
import uuid

st.set_page_config(page_title="Silver Tok v2.0", page_icon="🎬", layout="centered")

SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    try: return create_client(SUPABASE_URL, SUPABASE_KEY)
    except: return None

supabase = init_connection()
if supabase is None:
    st.error("Erro de conexão.")
    st.stop()

CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

if "usuario_logado" not in st.session_state: st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state: st.session_state.sala_ativa = None
if "id_upload_chat" not in st.session_state: st.session_state.id_upload_chat = str(uuid.uuid4())

if st.session_state.usuario_logado is None:
    st.title("🎬 Silver Tok & Chat 🔐")
    aba_auth = st.tabs(["Fazer Login", "Criar Nova Conta"])
    with aba_auth[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        if st.button("Entrar 🚀", key="btn_login", use_container_width=True):
            if login_user and login_senha:
                busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                if busca.data and busca.data[0]["senha"] == login_senha:
                    st.session_state.usuario_logado = busca.data[0]
                    st.success("Login feito!")
                    st.rerun()
                else: st.error("Incorreto.")
            else: st.warning("Preencha tudo!")
    with aba_auth[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie Senha:", type="password", key="cad_senha")
        cad_foto = st.file_uploader("Foto de Perfil:", type=["png", "jpg", "jpeg"], key="cad_foto")
        codigo_convite = st.text_input("🔑 Código Secreto:", type="password", key="codigo_convite")
        if st.button("Cadastrar Conta 🎉", key="btn_cad", use_container_width=True):
            if cad_user and cad_senha and codigo_convite == CHAVE_SECRETA:
                try:
                    url_foto = FOTO_PADRAO
                    if cad_foto:
                        nome_f = f"perfis/{uuid.uuid4()}.png"
                        supabase.storage.from_("imagens_chat").upload(nome_f, cad_foto.read())
                        url_foto = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                    supabase.table("perfis_usuarios").insert({"username": cad_user, "senha": cad_senha, "url_foto_perfil": url_foto}).execute()
                    st.success("Criado! Faça login.")
                except: st.error("Erro ou usuário já existe.")
            else: st.warning("Verifique os campos!")
else:
    user_atual = st.session_state.usuario_logado
    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=90)
    st.sidebar.write(f"Usuário: **{user_atual['username']}**")
    if st.sidebar.button("Sair 🚪", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.rerun()

    aba_feed, aba_chat = st.tabs(["📺 Silver Tok (Feed)", "💬 Chat-Exv"])
    with aba_feed:
        st.title("📺 Feed de Edits")
        with st.expander("➕ Publicar Vídeo por Link"):
            titulo_v = st.text_input("Legenda do Vídeo:", placeholder="Ex: Edit de Bleach! 🔥")
            url_v = st.text_input("Link do Vídeo (YouTube ou MP4 direto):", placeholder="https://www.youtube.com/watch?v=...")
            if st.button("Publicar 🚀", use_container_width=True):
                if url_v.strip() and titulo_v.strip():
                    try:
                        # Agora usando com segurança a coluna avatar_autor criada!
                        supabase.table("feed_videos").insert({
                            "titulo": titulo_v.strip(),
                            "url_video": url_v.strip(),
                            "username_autor": user_atual["username"],
                            "avatar_autor": user_atual.get("url_foto_perfil") or FOTO_PADRAO,
                            "curtidas": 0
                        }).execute()
                        st.success("Postado com sucesso!")
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao salvar no feed: {e}")
                else: st.warning("Preencha todos os campos!")
        try:
            dados = supabase.table("feed_videos").select("*").execute()
            if dados.data:
                for v in reversed(dados.data):
                    autor = v.get('username_autor', 'Membro')
                    img_autor = v.get('avatar_autor') or FOTO_PADRAO

                    col_img, col_txt = st.columns([1, 6])
                    with col_img: st.image(img_autor, width=40)
                    with col_txt: st.markdown(f"**@{autor}**")
                    st.caption(v["titulo"])
                    st.video(v["url_video"])
                    likes = v.get("curtidas", 0)
                    if st.button(f"❤️ {likes} Curtidas", key=f"lk_{v['id']}"):
                        supabase.table("feed_videos").update({"curtidas": likes + 1}).eq("id", v["id"]).execute()
                        st.rerun()
                    st.markdown("---")
        except: st.error("Erro ao carregar o feed.")

    with aba_chat:
        if st.session_state.sala_ativa is not None:
            st.title(f"💬 Sala Ativa")
            st.code(f"Código: {st.session_state.sala_ativa}")
            if st.button("⬅️ Voltar ao Menu", use_container_width=True):
                st.session_state.sala_ativa = None
                st.rerun()
            txt_m = st.text_input("Mensagem:", key="txt_msg_input")
            upload_img = st.file_uploader("Imagem (Opcional):", type=["png", "jpg", "jpeg", "gif"], key=st.session_state.id_upload_chat)
            if st.button("Enviar ✉️", use_container_width=True):
                if txt_m.strip() or upload_img:
                    url_img = None
                    if upload_img:
                        nome_f = f"chat/{uuid.uuid4()}.png"
                        supabase.storage.from_("imagens_chat").upload(nome_f, upload_img.read())
                        url_img = supabase.storage.from_("imagens_chat").get_public_url(nome_f)
                    supabase.table("bate-papo_profissional").insert({"id_usuario": user_atual["id"], "username": user_atual["username"], "url_foto_perfil": user_atual.get("url_foto_perfil") or FOTO_PADRAO, "mensagem": txt_m.strip() if txt_m.strip() else None, "url_imagem_enviada": url_img, "codigo_sala": st.session_state.sala_ativa}).execute()
                    st.session_state.id_upload_chat = str(uuid.uuid4())
                    st.rerun()
            try:
                res = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).execute()
                if res.data:
                    for m in reversed(res.data[-40:]):
                        c1, c2 = st.columns([1, 6])
                        with c1: st.image(m.get("url_foto_perfil") or FOTO_PADRAO, width=40)
                        with c2:
                            st.markdown(f"**{m['username']}**")
                            if m.get("mensagem"): st.write(m["mensagem"])
                            if m.get("url_imagem_enviada"): st.image(m["url_imagem_enviada"], use_container_width=True)
                        st.markdown("---")
            except: st.write("Erro ao carregar.")
        else:
            st.title("🎛️ Painel Chat-Exv")
            m_tabs = st.tabs(["💬 Privado", "👨‍👩‍👦 Novo Grupo", "🔑 Entrar", "👥 Amigos", "➕ Adicionar"])
            with m_tabs[0]:
                try:
                    amg = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    nomes = []
                    m_ids = {}
                    for a in amg.data:
                        o_id = a["id_usuario_recebe"] if str(a["id_usuario_envio"]) == str(user_atual["id"]) else a["id_usuario_envio"]
                        du = supabase.table("perfis_usuarios").select("username").eq("id", o_id).execute()
                        if du.data:
                            n = du.data[0]["username"]
                            nomes.append(n)
                            m_ids[n] = o_id
                    if nomes:
                        alvo = st.selectbox("Amigo:", nomes)
                        if st.button("Abrir Conversa Particular 🚀", use_container_width=True):
                            ids = sorted([str(user_atual["id"]), str(m_ids[alvo])])
                            st.session_state.sala_ativa = f"PRIVADO-{ids[0][:8]}-{ids[1][:8]}"
                            st.rerun()
                    else: st.info("Sem amigos aceitos.")
                except: st.write("Erro.")
            with m_tabs[1]:
                n_grp = st.text_input("Grupo:")
                if st.button("Criar Grupo 🎉", use_container_width=True) and n_grp:
                    cod = f"GRUPO-{str(uuid.uuid4())[:8].upper()}"
                    supabase.table("salas_chat").insert({"codigo_sala": cod, "nome_sala": n_grp, "tipo": "grupo"}).execute()
                    st.success(f"Código: {cod}")
            with m_tabs[2]:
                cod_d = st.text_input("Código:").strip().upper()
                if st.button("Entrar 🚪", use_container_width=True) and cod_d:
                    st.session_state.sala_ativa = cod_d
                    st.rerun()
            with m_tabs[3]:
                try:
                    peds = supabase.table("lista_amigos").select("*").eq("id_usuario_recebe", user_atual["id"]).eq("status", "pendente").execute()
                    for p in peds.data:
                        dr = supabase.table("perfis_usuarios").select("username").eq("id", p["id_usuario_envio"]).execute()
                        if dr.data:
                            st.write(f"Pedido de: **{dr.data[0]['username']}**")
                            if st.button("Aceitar", key=f"ac_{p['id']}"):
                                supabase.table("lista_amigos").update({"status": "aceito"}).eq("id", p["id"]).execute()
                                st.rerun()
                    conf = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                    for c in conf.data:
                        o_id = c["id_usuario_recebe"] if str(c["id_usuario_envio"]) == str(user_atual["id"]) else c["id_usuario_envio"]
                        du = supabase.table("perfis_usuarios").select("username").eq("id", o_id).execute()
                        if du.data: st.write(f"🟢 {du.data[0]['username']}")
                except: pass
            with m_tabs[4]:
                b_amg = st.text_input("Usuário para adicionar:").strip()
                if st.button("Enviar Pedido ➕", use_container_width=True) and b_amg:
                    try:
                        alvo = supabase.table("perfis_usuarios").select("*").eq("username", b_amg).execute()
                        if alvo.data:
                            if str(alvo.data[0]["id"]) == str(user_atual["id"]): st.error("Não pode se adicionar!")
                            else:
                                supabase.table("lista_amigos").insert({"id_usuario_envio": user_atual["id"], "id_usuario_recebe": alvo.data[0]["id"], "status": "pendente"}).execute()
                                st.success("Enviado!")
                        else: st.error("Não encontrado.")
                    except: st.error("Erro.")
                        

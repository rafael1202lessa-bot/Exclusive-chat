import streamlit as st
from supabase import create_client, Client
import uuid

# Configuração da página do Chat
st.set_page_config(page_title="Super Chat da Galera", page_icon="💬", layout="centered")

# --- CONEXÃO COM O SEU BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Erro de conexão com o servidor.")

# --- CONFIGURAÇÕES GERAIS ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# Inicialização de sessões (State)
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None
if "id_upload" not in st.session_state:
    st.session_state.id_upload = str(uuid.uuid4())

# --- FUNÇÃO PARA APAGAR MENSAGEM ---
def apagar_mensagem(id_mensagem):
    try:
        supabase.table("bate-papo_profissional").delete().eq("id", id_mensagem).execute()
        st.toast("Mensagem apagada! 🗑️")
    except Exception as e:
        st.error("Erro ao deletar a mensagem.")

# --- TELA DE AUTENTICAÇÃO (LOGIN / CADASTRO) ---
if st.session_state.usuario_logado is None:
    st.title("🔐 Bem-vindo ao Super Chat")
    aba = st.tabs(["Fazer Login", "Criar Nova Conta"])
    
    with aba[0]:
        st.subheader("Acesse sua Conta")
        login_user = st.text_input("Usuário:", key="login_user").strip()
        login_senha = st.text_input("Senha:", type="password", key="login_senha")
        
        if st.button("Entrar 🚀", key="btn_login"):
            if login_user and login_senha:
                try:
                    busca = supabase.table("perfis_usuarios").select("*").eq("username", login_user).execute()
                    if busca.data and busca.data[0]["senha"] == login_senha:
                        st.session_state.usuario_logado = busca.data[0]
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
                except Exception as e:
                    st.error("Erro ao conectar ao banco de dados.")
            else:
                st.warning("Preencha todos os campos!")

    with aba[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha um Nome de Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        cad_foto = st.file_uploader("Escolha sua Foto de Perfil (Opcional):", type=["png", "jpg", "jpeg"], key="cad_foto")
        codigo_convite = st.text_input("🔑 Código de Convite Secreto:", type="password", key="codigo_convite")
        
        if st.button("Cadastrar Conta 🎉", key="btn_cad"):
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
                    except Exception as e:
                        st.error("Este nome de usuário já existe ou ocorreu um erro.")
            else:
                st.warning("Usuário e senha são obrigatórios!")

# --- FLUXO PRINCIPAL APÓS LOGIN ---
else:
    user_atual = st.session_state.usuario_logado
    
    # Barra lateral de Perfil
    st.sidebar.image(user_atual.get("url_foto_perfil") or FOTO_PADRAO, width=100)
    st.sidebar.write(f"Logado como: **{user_atual['username']}**")
    if st.sidebar.button("Sair da Conta 🚪"):
        st.session_state.usuario_logado = None
        st.session_state.sala_ativa = None
        st.rerun()

    # --- TELA INTERNA DO CHAT (SALA ATIVA) ---
    if st.session_state.sala_ativa is not None:
        st.title(f"💬 Sala Ativa")
        st.code(f"Código da Sala: {st.session_state.sala_ativa}")
        
        if st.button("⬅️ Voltar para o Menu Principal"):
            st.session_state.sala_ativa = None
            st.rerun()
            
        st.markdown("---")

        # Área de Envio de Mensagem para a Sala específica
        with st.container():
            txt_msg = st.text_input("Digite sua mensagem:", placeholder="Escreva algo aqui...", key="txt_msg_input")
            upload_img = st.file_uploader("Enviar uma Imagem (Opcional):", type=["png", "jpg", "jpeg", "gif"], key=st.session_state.id_upload)
            
            if st.button("Enviar Mensagem ✉️"):
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
                            "url_foto_perfil": user_atual["url_foto_perfil"],
                            "mensagem": txt_msg.strip() if txt_msg.strip() else None,
                            "url_imagem_enviada": url_img_enviada,
                            "codigo_sala": st.session_state.sala_ativa
                        }).execute()
                        
                        st.session_state.id_upload = str(uuid.uuid4())
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao enviar mensagem.")
                else:
                    st.warning("Escreva um texto ou selecione uma imagem!")

        st.markdown("---")
        st.subheader("📋 Histórico da Sala")

        # Exibição do histórico filtrado pelo código da sala ativa
        try:
            resposta = supabase.table("bate-papo_profissional").select("*").eq("codigo_sala", st.session_state.sala_ativa).order("criado_em", desc=True).limit(40).execute()
            if resposta.data:
                for msg in resposta.data:
                    col1, col2, col3 = st.columns([1, 5, 1])
                    with col1:
                        st.image(msg.get("url_foto_perfil") or FOTO_PADRAO, width=50)
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
                st.write("Nenhuma mensagem por aqui ainda.")
        except Exception as e:
            st.write("Nenhuma mensagem registrada nesta sala.")

    # --- TELA DO MENU PRINCIPAL (AS 5 OPÇÕES) ---
    else:
        st.title("🎛️ Painel de Controle")
        menu = st.tabs([
            "💬 Criar Conversa", 
            "👨‍👩‍👦 Criar Grupo", 
            "🔑 Entrar com Código",
            "📋 Lista de Amigos", 
            "➕ Adicionar Amigo"
        ])
        
        # 1️⃣ CRIAR CONVERSA (1 PARA 1)
        with menu[0]:
            st.subheader("Iniciar Chat Privado")
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
                    if st.button("Abrir Conversa Particular 🚀"):
                        ids_ordenados = sorted([str(user_atual["id"]), str(mapa_ids[alvo])])
                        cod_sala_unica = f"PRIVADO-{ids_ordenados[0][:8]}-{ids_ordenados[1][:8]}"
                        st.session_state.sala_ativa = cod_sala_unica
                        st.rerun()
                else:
                    st.info("Você ainda não possui amigos aceitos para conversar.")
            except:
                st.write("Erro ao carregar amigos.")

        # 2️⃣ CRIAR CONVERSA EM GRUPO
        with menu[1]:
            st.subheader("Criar Novo Grupo")
            nome_novo_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Resenha da Galera")
            if st.button("Criar e Gerar Código do Grupo 🎉"):
                if nome_novo_grupo:
                    novo_codigo = f"GRUPO-{str(uuid.uuid4())[:8].upper()}"
                    try:
                        supabase.table("salas_chat").insert({"codigo_sala": novo_codigo, "nome_sala": nome_novo_grupo, "tipo": "grupo"}).execute()
                        supabase.table("membros_salas").insert({"codigo_sala": novo_codigo, "id_usuario": user_atual["id"]}).execute()
                        st.success(f"Grupo criado! Compartilhe o código com os amigos: **{novo_codigo}**")
                    except:
                        st.error("Erro ao registrar grupo.")
                else:
                    st.warning("Digite um nome para o grupo!")

        # 3️⃣ ENTRAR COM CÓDIGO DA SALA
        with menu[2]:
            st.subheader("Entrar em uma Sala Existente")
            codigo_digitado = st.text_input("Insira o Código da Sala:", placeholder="Ex: GRUPO-A8F2B9D1").strip().upper()
            if st.button("Entrar na Sala 🚪"):
                if codigo_digitado:
                    st.session_state.sala_ativa = codigo_digitado
                    st.rerun()
                else:
                    st.warning("Por favor, digite um código.")

        # 4️⃣ LISTA DE AMIGOS
        with menu[3]:
            st.subheader("Seus Amigos e Solicitações")
            try:
                pedidos = supabase.table("lista_amigos").select("*").eq("id_usuario_recebe", user_atual["id"]).eq("status", "pendente").execute()
                if pedidos.data:
                    st.write("📥 **Solicitações Recebidas:**")
                    for ped in pedidos.data:
                        dados_remetente = supabase.table("perfis_usuarios").select("username").eq("id", ped["id_usuario_envio"]).execute()
                        if dados_remetente.data:
                            nome_remetente = dados_remetente.data[0]["username"]
                            col_n, col_a = st.columns([3, 1])
                            with col_n:
                                st.write(f"Pedido de: **{nome_remetente}**")
                            with col_a:
                                if st.button("Aceitar ✅", key=f"aceitar_{ped['id']}"):
                                    supabase.table("lista_amigos").update({"status": "aceito"}).eq("id", ped["id"]).execute()
                                    st.rerun()
                
                confirmados = supabase.table("lista_amigos").select("*").or_(f"id_usuario_envio.eq.{user_atual['id']},id_usuario_recebe.eq.{user_atual['id']}").eq("status", "aceito").execute()
                if confirmados.data:
                    st.write("👥 **Seus Amigos Conectados:**")
                    for amg in confirmados.data:
                        outro_id = amg["id_usuario_recebe"] if str(amg["id_usuario_envio"]) == str(user_atual["id"]) else amg["id_usuario_envio"]
                        dados_u = supabase.table("perfis_usuarios").select("username").eq("id", outro_id).execute()
                        if dados_u.data:
                            st.write(f"🟢 **{dados_u.data[0]['username']}**")
                else:
                    st.caption("Você ainda não tem amigos adicionados.")
            except:
                st.caption("Nenhum amigo adicionado ainda.")

        # 5️⃣ ADICIONAR AMIGO
        with menu[4]:
            st.subheader("Procurar Novos Amigos")
            buscar_amigo = st.text_input("Digite exatamente o nome de usuário do seu amigo:", placeholder="Ex: Carlos123").strip()
            if st.button("Enviar Solicitação de Amizade ➕"):
                if buscar_amigo:
                    try:
                        alvo_user = supabase.table("perfis_usuarios").select("*").eq("username", buscar_amigo).execute()
                        if alvo_user.data:
                            id_alvo = alvo_user.data[0]["id"]
                            if str(id_alvo) == str(user_atual["id"]):
                                st.error("Você não pode adicionar a si mesmo!")
                            else:
                                supabase.table("lista_amigos").insert({
                                    "id_usuario_envio": user_atual["id"],
                                    "id_usuario_recebe": id_alvo,
                                    "status": "pendente"
                                }).execute()
                                st.success(f"Solicitação enviada para **{buscar_amigo}**!")
                        else:
                            st.error("Usuário não encontrado!")
                    except:
                        st.error("Erro ao processar solicitação.")
                else:
                    st.warning("Digite um nome de usuário.")
        

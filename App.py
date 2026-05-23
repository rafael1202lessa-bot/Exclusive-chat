import streamlit as st
from supabase import create_client, Client
import uuid

# Configuração da página do Chat
st.set_page_config(page_title="Super Chat da Galera", page_icon="💬", layout="centered")

# --- CONEXÃO COM O SEU BANCO DE DADOS ---
SUPABASE_URL = "https://ldjtqgeyorkzbvuichjj.supabase.co"
SUPABASE_KEY = "sb_publishable_ZWY9Hp6kQrhOzff6xc_DrA_8TlnrqQ_"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("Erro de conexão com o servidor.")

# --- CHAVE DE CONVITE SECRETA ---
CHAVE_SECRETA = "ChatPrivado2026"

# Foto padrão para quem não escolher uma foto de perfil
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# Controle de sessão (gerenciamento de login)
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# Cria um gerador de chaves para resetar o campo de upload de imagem
if "id_upload" not in st.session_state:
    st.session_state.id_upload = str(uuid.uuid4())

# --- FUNÇÃO PARA APAGAR UMA MENSAGEM ---
def apagar_mensagem(id_mensagem):
    try:
        supabase.table("bate-papo_profissional").delete().eq("id", id_mensagem).execute()
        # Não precisa de st.rerun aqui porque o clique no botão já recarrega a página por padrão
    except Exception as e:
        st.error("Erro ao deletar a mensagem no banco de dados.")

# --- FUNÇÃO DE CALLBACK PARA ENVIAR MENSAGEM ---
def enviar_mensagem_chat():
    msg_texto = st.session_state.get("txt_msg_temp", "").strip()
    msg_foto = st.session_state.get("upload_img_temp", None)
    user_atual = st.session_state.usuario_logado
    
    # Se o file_uploader tiver um arquivo, precisamos ler ele antes de limpar o formulário
    # O Streamlit às vezes perde a referência do arquivo no callback 'clear_on_submit'
    # Por isso, vamos guardar os bytes na sessão se houver imagem
    if msg_foto:
        st.session_state["foto_bytes_temp"] = msg_foto.read()
        st.session_state["foto_nome_temp"] = msg_foto.name
    else:
        st.session_state["foto_bytes_temp"] = None

    foto_bytes = st.session_state.get("foto_bytes_temp", None)
    
    if msg_texto != "" or foto_bytes is not None:
        try:
            url_img_enviada = None
            
            if foto_bytes:
                extensao = st.session_state["foto_nome_temp"].split(".")[-1]
                nome_arquivo = f"chat/{uuid.uuid4()}.{extensao}"
                supabase.storage.from_("imagens_chat").upload(nome_arquivo, foto_bytes)
                url_img_enviada = supabase.storage.from_("imagens_chat").get_public_url(nome_arquivo)
            
            supabase.table("bate-papo_profissional").insert({
                "id_usuario": user_atual["id"],
                "username": user_atual["username"],
                "url_foto_perfil": user_atual["url_foto_perfil"],
                "mensagem": msg_texto if msg_texto else None,
                "url_imagem_enviada": url_img_enviada
            }).execute()
            
            # Força o campo de foto a limpar gerando uma nova chave
            st.session_state.id_upload = str(uuid.uuid4())
            
        except Exception as e:
            st.error("Erro ao enviar para o banco de dados.")

# --- TELA DE AUTENTICAÇÃO (LOGIN / CADASTRO) ---
if st.session_state.usuario_logado is None:
    st.title("🔐 Bem-vindo ao Super Chat")
    
    aba = st.tabs(["Fazer Login", "Criar Nova Conta"])
    
    # --- ABA 1: LOGIN ---
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

    # --- ABA 2: CADASTRO ---
    with aba[1]:
        st.subheader("Crie seu Perfil")
        cad_user = st.text_input("Escolha um Nome de Usuário:", key="cad_user").strip()
        cad_senha = st.text_input("Crie uma Senha:", type="password", key="cad_senha")
        cad_foto = st.file_uploader("Escolha sua Foto de Perfil (Opcional):", type=["png", "jpg", "jpeg"], key="cad_foto")
        codigo_convite = st.text_input("🔑 Código de Convite Secreto:", type="password", key="codigo_convite")
        
        if st.button("Cadastrar Conta 🎉", key="btn_cad"):
            if cad_user and cad_senha:
                if codigo_convite != CHAVE_SECRETA:
                    st.error("❌ Código de Convite incorreto! Você não tem permissão para se cadastrar.")
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
                        
                        st.success("Conta criada! Agora faça o login na primeira aba.")
                    except Exception as e:
                        st.error("Este nome de usuário já existe ou ocorreu um erro no servidor.")
            else:
                st.warning("Usuário e senha são obrigatórios!")

# --- TELA DO CHAT PRINCIPAL ---
else:
    user_atual = st.session_state.usuario_logado
    st.title("💬 Chat Oficial Profissional")
    
    # Barra lateral com dados do perfil
    st.sidebar.image(user_atual["url_foto_perfil"], width=100)
    st.sidebar.write(f"Logado como: **{user_atual['username']}**")
    if st.sidebar.button("Sair da Conta 🚪"):
        st.session_state.usuario_logado = None
        st.rerun()
        
    st.markdown("---")

    # --- ENVIAR MENSAGEM OU FOTO ---
    with st.form(key="form_chat_novo", clear_on_submit=True):
        st.text_input("Digite sua mensagem:", placeholder="Escreva algo aqui...", key="txt_msg_temp")
        st.file_uploader("Enviar uma Imagem no Chat (Opcional):", type=["png", "jpg", "jpeg", "gif"], key=st.session_state.id_upload, name="upload_img_temp")
        
        st.form_submit_button(label="Enviar para a Galera ✉️", on_click=enviar_mensagem_chat)

    st.markdown("---")
    st.subheader("📋 Histórico do Chat")

    # --- EXIBIÇÃO DAS MENSAGENS COM BOTOES DE DELETAR ---
    try:
        resposta = supabase.table("bate-papo_profissional").select("*").order("criado_em", desc=True).limit(40).execute()
        
        if resposta.data:
            for msg in resposta.data:
                # Criamos 3 colunas: 1 para foto de perfil, 1 para o conteúdo e 1 para o botão de apagar
                col1, col2, col3 = st.columns([1, 5, 1])
                
                with col1:
                    foto_user = msg.get("url_foto_perfil") or FOTO_PADRAO
                    st.image(foto_user, width=45)
                
                with col2:
                    st.markdown(f"**{msg['username']}**")
                    if msg.get("mensagem"):
                        st.write(msg["mensagem"])
                    if msg.get("url_imagem_enviada"):
                        st.image(msg["url_imagem_enviada"], use_container_width=True)
                
                with col3:
                    # SEGURANÇA: Só mostra o botão se a mensagem for do próprio usuário logado
                    if str(msg.get("id_usuario")) == str(user_atual["id"]):
                        st.button("🗑️", key=f"del_{msg['id']}", on_click=apagar_mensagem, args=(msg['id'],))
                        
                st.markdown("---")
        else:
            st.write("Nenhuma mensagem por aqui. Seja o primeiro a falar!")
            
    except Exception as e:
        st.write("Aguardando carregamento das conversas...")
    

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

# --- CONFIGURAÇÕES GERAIS ---
CHAVE_SECRETA = "ChatPrivado2026"
FOTO_PADRAO = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

# Controle de sessão (gerenciamento de login)
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# Controla em qual sala o usuário está (None significa que ele está no Menu Principal)
if "sala_ativa" not in st.session_state:
    st.session_state.sala_ativa = None

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

    # --- SE O USUÁRIO JÁ ESTIVER DENTRO DE UMA SALA ---
    if st.session_state.sala_ativa is not None:
        st.title(f"💬 Sala: {st.session_state.sala_ativa}")
        if st.button("⬅️ Voltar para o Menu Principal"):
            st.session_state.sala_ativa = None
            st.rerun()
            
        st.write("*O histórico específico desta sala aparecerá aqui no próximo passo...*")

    # --- SE O USUÁRIO ESTIVER NO MENU PRINCIPAL (AS 5 OPÇÕES) ---
    else:
        st.title("🎛️ Painel de Controle")
        st.markdown("Escolha o que deseja fazer hoje:")
        
        # Criação das abas para as 5 opções do menu
        menu = st.tabs([
            "💬 Criar Conversa", 
            "👨‍👩‍👦 Criar Grupo", 
            "🔑 Entrar com Código",
            "📋 Lista de Amigos", 
            "➕ Adicionar Amigo"
        ])
        
        # 1️⃣ ABA: CRIAR CONVERSA (1 PARA 1)
        with menu[0]:
            st.subheader("Iniciar Chat Privado")
            st.caption("Selecione um amigo abaixo para abrir o chat particular.")
            # Exemplo visual (será dinâmico)
            st.selectbox("Escolha um amigo da lista:", ["Nenhum amigo online", "Exemplo_Amigo1", "Exemplo_Amigo2"])
            if st.button("Abrir Conversa Particular 🚀"):
                st.info("Função integrada em breve!")

        # 2️⃣ ABA: CRIAR CONVERSA EM GRUPO
        with menu[1]:
            st.subheader("Criar Novo Grupo")
            nome_novo_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Resenha do Fim de Semana")
            st.multiselect("Selecione os amigos para adicionar ao grupo:", ["Amigo_1", "Amigo_2", "Amigo_3"])
            if st.button("Criar e Gerar Código do Grupo 🎉"):
                if nome_novo_grupo:
                    codigo_gerado = str(uuid.uuid4())[:8].upper() # Gera um código curto de 8 dígitos
                    st.success(f"Grupo criado! Compartilhe o código com os amigos: **{codigo_gerado}**")
                else:
                    st.warning("Digite um nome para o grupo!")

        # 3️⃣ ABA: ENTRAR COM CÓDIGO DA SALA (A que você pediu!)
        with menu[2]:
            st.subheader("Entrar em uma Sala Existente")
            st.markdown("Recebeu um código de grupo ou de uma conversa privada? Digite ele aqui para se juntar à conversa.")
            codigo_digitado = st.text_input("Insira o Código da Sala:", placeholder="Ex: A8F2B9D1").strip().upper()
            
            if st.button("Entrar na Sala 🚪"):
                if codigo_digitado:
                    st.session_state.sala_ativa = codigo_digitado
                    st.success(f"Entrando na sala {codigo_digitado}...")
                    st.rerun()
                else:
                    st.warning("Por favor, digite um código válido.")

        # 4️⃣ ABA: LISTA DE AMIGOS
        with menu[3]:
            st.subheader("Seus Amigos")
            # Exemplo visual de como ficará listado
            st.write("🟢 **Amigo_Exemplo_1** - *Disponível para conversar*")
            st.write("🟡 **Amigo_Exemplo_2** - *Não incomodar*")

        # 5️⃣ ABA: ADICIONAR AMIGO
        with menu[4]:
            st.subheader("Procurar Novos Amigos")
            buscar_amigo = st.text_input("Digite o nome de usuário do seu amigo:", placeholder="Ex: Rafael_oficial_2").strip()
            if st.button("Enviar Solicitação de Amizade ➕"):
                if buscar_amigo:
                    st.success(f"Solicitação enviada para **{buscar_amigo}**!")
                else:
                    st.warning("Digite um nome de usuário.")
                    

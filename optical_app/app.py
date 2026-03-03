import streamlit as st
import os

# Set page configuration
st.set_page_config(
    page_title="Sistema Ótica Shirlene",
    page_icon="👓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
    }
    
    /* Hide "press enter to submit" message */
    .stForm [data-testid="InputInstructions"],
    .stForm .stMarkdown small,
    [data-testid="stFormSubmitButton"] + div small {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Home", "Clientes", "📋 Receitas"])

# --- Navigation State Cleanup ---
if 'last_page' not in st.session_state:
    st.session_state.last_page = page

if st.session_state.last_page != page:
    # Cleanup when changing pages
    keys_to_clear = [
        'active_prescription_client', 
        'new_prescription_expander_open', 
        'edit_data', # Generic edit data holder? No, usually specific like edit_data_{id}
        'editing_prescription_id' # If used
    ]
    # Also clean dynamic keys if possible, but let's stick to known state variables
    for key in list(st.session_state.keys()):
        if key in keys_to_clear or key.startswith('editing_inline_') or key.startswith('edit_data_') or key.startswith('new_prof_'):
             del st.session_state[key]
    
    st.session_state.last_page = page


if page == "Home":
    st.title("👓 Sistema de Gestão - Ótica Shirlene")
    st.write("Bem-vindo ao sistema de gestão.")
    st.info("Selecione uma opção no menu lateral para começar.")

elif page == "Clientes":
    from modules import clients
    clients.show()

elif page == "📋 Receitas":
    from modules import prescriptions
    prescriptions.show()

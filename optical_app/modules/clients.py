import streamlit as st
import pandas as pd
import time
from datetime import datetime
from modules import prescriptions
from modules.database import get_supabase

def init_db():
    """No longer needed - tables are created directly in Supabase."""
    pass

def add_client(name, sex, phones_list, email, cpf, rg, birth_date, address, address_number, neighborhood, notes):
    sb = get_supabase()
    bdate_str = str(birth_date) if birth_date else None

    result = sb.table('clients').insert({
        'name': name, 'sex': sex, 'email': email, 'cpf': cpf, 'rg': rg,
        'birth_date': bdate_str, 'address': address, 'address_number': address_number,
        'neighborhood': neighborhood, 'notes': notes
    }).execute()

    client_id = result.data[0]['id']

    for phone in phones_list:
        if phone['number']:
            sb.table('client_phones').insert({
                'client_id': client_id,
                'number': phone['number'],
                'complement': phone.get('complement', '')
            }).execute()

    time.sleep(2)  # Wait for animation to complete
    st.rerun()


def get_clients():
    sb = get_supabase()
    clients_res = sb.table('clients').select('*').order('created_at', desc=True).execute()
    phones_res = sb.table('client_phones').select('client_id, number, complement').execute()

    df = pd.DataFrame(clients_res.data)
    phones_df = pd.DataFrame(phones_res.data)

    if not df.empty and not phones_df.empty:
        phones_df['display'] = phones_df.apply(
            lambda x: f"{x['number']} ({x['complement']})" if x['complement'] else x['number'], axis=1
        )
        grouped_phones = phones_df.groupby('client_id')['display'].apply(list).reset_index()
        df = pd.merge(df, grouped_phones, left_on='id', right_on='client_id', how='left')
        df['phone_display'] = df['display'].apply(lambda x: ", ".join(x) if isinstance(x, list) else "")
    else:
        df['phone_display'] = ""

    return df

def get_client_phones(client_id):
    sb = get_supabase()
    res = sb.table('client_phones').select('*').eq('client_id', client_id).execute()
    return pd.DataFrame(res.data)

def update_client(id, name, sex, phones_list, email, cpf, rg, birth_date, address, address_number, neighborhood, notes):
    sb = get_supabase()
    bdate_str = str(birth_date) if birth_date else None

    sb.table('clients').update({
        'name': name, 'sex': sex, 'email': email, 'cpf': cpf, 'rg': rg,
        'birth_date': bdate_str, 'address': address, 'address_number': address_number,
        'neighborhood': neighborhood, 'notes': notes
    }).eq('id', id).execute()

    # Phones: delete and re-insert
    sb.table('client_phones').delete().eq('client_id', id).execute()
    for phone in phones_list:
        if phone['number']:
            sb.table('client_phones').insert({
                'client_id': id,
                'number': phone['number'],
                'complement': phone.get('complement', '')
            }).execute()

    st.rerun()

def delete_client(id):
    sb = get_supabase()
    # Phones deleted via ON DELETE CASCADE in Supabase
    sb.table('clients').delete().eq('id', id).execute()
    st.success("Cliente excluído com sucesso!")
    st.rerun()


@st.dialog("Editar Cliente")
def edit_client_dialog(client_data):
    # Clear any previous delete confirmation state when opening dialog
    if 'confirm_delete_client' in st.session_state:
        del st.session_state.confirm_delete_client
    
    # Fetch existing phones
    existing_phones_df = get_client_phones(client_data['id'])
    phones_list = existing_phones_df.to_dict('records')
    
    # Ensure at least one empty slot if none exist (though rare)
    if not phones_list:
        phones_list = [{'number': '', 'complement': ''}]

    with st.form("edit_client_form"):
        # Header Info
        # Format created_at to BR format
        created_at_fmt = client_data['created_at']
        try:
            dt_obj = datetime.strptime(client_data['created_at'], '%Y-%m-%d %H:%M:%S')
            created_at_fmt = dt_obj.strftime('%d/%m/%Y %H:%M')
        except:
            pass # Keep original if parsing fails
            
        st.caption(f"Data do Cadastro: {created_at_fmt}")
        new_name = st.text_input("Nome Completo", value=client_data['name'])
        
        # Sex Radio
        sex_options = ["Masculino", "Feminino"]
        current_sex_index = 0
        if client_data['sex'] in sex_options:
            current_sex_index = sex_options.index(client_data['sex'])
        new_sex = st.radio("Sexo", sex_options, index=current_sex_index, horizontal=True)

        col1, col2 = st.columns(2)
        with col1:
            new_cpf = st.text_input("CPF", value=client_data['cpf'] if client_data['cpf'] else "")
        with col2:
            new_rg = st.text_input("RG", value=client_data['rg'] if client_data['rg'] else "")
            
        col3, col4 = st.columns(2)
        with col3:
            # Handle date conversion safely
            default_date = None
            if client_data['birth_date'] and client_data['birth_date'] != 'None':
                try:
                    default_date = datetime.strptime(client_data['birth_date'], '%Y-%m-%d').date()
                except:
                    pass
            new_birth_date = st.date_input("Data de Nascimento", value=default_date, format="DD/MM/YYYY")
        with col4:
            new_email = st.text_input("E-mail", value=client_data['email'])

        st.subheader("Contatos")
        
        updated_phones = []
        for i, phone in enumerate(phones_list):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                p_num = st.text_input(f"Telefone {i+1}", value=phone['number'], key=f"edit_phone_{i}")
            with c_p2:
                p_comp = st.text_input(f"Complemento {i+1}", value=phone['complement'], key=f"edit_comp_{i}")
            updated_phones.append({'number': p_num, 'complement': p_comp})
            
        # Extra Type
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            new_p_num = st.text_input("Novo Telefone", key="new_phone_edit")
        with c_p2:
            new_p_comp = st.text_input("Novo Complemento", key="new_comp_edit")
        if new_p_num:
             updated_phones.append({'number': new_p_num, 'complement': new_p_comp})

        st.subheader("Endereço")
        col_addr1, col_addr2 = st.columns([3, 1])
        with col_addr1:
            new_address = st.text_input("Logradouro (Rua, Av.)", value=client_data['address'] if client_data['address'] else "")
        with col_addr2:
            new_address_number = st.text_input("Número", value=client_data['address_number'] if client_data['address_number'] else "")
        
        new_neighborhood = st.text_input("Bairro", value=client_data['neighborhood'] if client_data['neighborhood'] else "")

        new_notes = st.text_area("Observações", value=client_data['notes'])
        
        st.caption(f"Saldo em Vale: R$ {client_data['credit_balance'] if client_data['credit_balance'] else 0.00:.2f} (Calculado automaticamente)")

        col_save, col_del = st.columns([1, 1])
        with col_save:
            if st.form_submit_button("Salvar Alterações"):
                update_client(client_data['id'], new_name, new_sex, updated_phones, new_email, new_cpf, new_rg, new_birth_date, new_address, new_address_number, new_neighborhood, new_notes)
        with col_del:
            delete_clicked = st.form_submit_button("🗑️ Excluir Cliente", type="secondary")
            if delete_clicked:
                st.session_state.confirm_delete_client = client_data['id']
    
    # Delete confirmation outside form
    if 'confirm_delete_client' in st.session_state:
        st.warning("⚠️ **Confirmar Exclusão**")
        st.write(f"Tem certeza que deseja excluir o cliente **{client_data['name']}**?")
        st.caption("⚠️ Esta ação não pode ser desfeita!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sim, excluir", type="primary", key="confirm_yes"):
                delete_client(st.session_state.confirm_delete_client)
                del st.session_state.confirm_delete_client
        with col2:
            if st.button("❌ Cancelar", key="confirm_no"):
                del st.session_state.confirm_delete_client
                st.rerun()
        
        # Auto-scroll to show confirmation buttons
        st.components.v1.html("""
            <script>
                setTimeout(() => {
                    window.parent.document.querySelector('[data-testid="stDialog"]').scrollTop = 999999;
                }, 100);
            </script>
        """, height=0, width=0)

def show():
    init_db()
    
    # Prevent Enter key form submission + Success Animation
    st.components.v1.html("""
        <style>
            .success-message {
                color: #22c55e;
                font-size: 0.85em;
                margin-top: 8px;
                text-align: center;
                animation: fadeInOut 2s ease-in-out;
                font-weight: 500;
            }
            
            @keyframes fadeInOut {
                0% { opacity: 0; transform: translateY(-5px); }
                15% { opacity: 1; transform: translateY(0); }
                85% { opacity: 1; transform: translateY(0); }
                100% { opacity: 0; transform: translateY(-5px); }
            }
        </style>
        <script>
            function preventEnterSubmit() {
                const inputs = window.parent.document.querySelectorAll('input');
                inputs.forEach(input => {
                    // Skip search input - allow Enter to trigger search
                    if (input.placeholder && input.placeholder.includes('Pesquisar Cliente')) {
                        return; // Don't prevent Enter on search field
                    }
                    
                    if (!input.dataset.enterPrevented) {
                        input.dataset.enterPrevented = 'true';
                        input.addEventListener('keydown', function(e) {
                            if (e.key === 'Enter' || e.keyCode === 13) {
                                e.preventDefault();
                                return false;
                            }
                        });
                    }
                });
            }
            
            function attachSuccessAnimation() {
                const buttons = window.parent.document.querySelectorAll('button[kind="primaryFormSubmit"]');
                buttons.forEach(button => {
                    // Exclude delete buttons
                    const buttonText = button.textContent.toLowerCase();
                    if (buttonText.includes('excluir') || buttonText.includes('deletar')) {
                        return; // Skip delete buttons
                    }
                    
                    if (!button.dataset.animationAttached) {
                        button.dataset.animationAttached = 'true';
                        button.addEventListener('click', function(e) {
                            // Add inline style for better visibility
                            const originalStyle = this.style.cssText;
                            
                            // Apply green border animation
                            this.style.outline = '4px solid #22c55e';
                            this.style.outlineOffset = '3px';
                            this.style.transition = 'outline 0.3s ease-in-out, outline-offset 0.3s ease-in-out';
                            
                            // Create and show success message below the button
                            let successMsg = this.parentElement.querySelector('.success-message');
                            if (!successMsg) {
                                successMsg = document.createElement('div');
                                successMsg.className = 'success-message';
                                successMsg.textContent = 'Salvo com sucesso!';
                                this.parentElement.appendChild(successMsg);
                            } else {
                                successMsg.style.display = 'block';
                                // Trigger reflow to restart animation
                                successMsg.style.animation = 'none';
                                setTimeout(() => {
                                    successMsg.style.animation = 'fadeInOut 2s ease-in-out';
                                }, 10);
                            }
                            
                            // Animate out border
                            setTimeout(() => {
                                this.style.outline = '4px solid rgba(34, 197, 94, 0)';
                                this.style.outlineOffset = '0px';
                            }, 1500);
                            
                            // Remove styles after animation
                            setTimeout(() => {
                                this.style.cssText = originalStyle;
                            }, 2000);
                        });
                    }
                });
            }
            
            // Run on load
            preventEnterSubmit();
            attachSuccessAnimation();
            
            // Run periodically to catch dynamically added inputs (optimized to 2s)
            setInterval(() => {
                preventEnterSubmit();
                attachSuccessAnimation();
            }, 2000);
        </script>
    """, height=0, width=0)
    
    st.title("👥 Gestão de Clientes")

    tab1, tab2 = st.tabs(["Novo Cliente", "Lista de Clientes"])

    with tab1:
        st.header("Cadastrar Novo Cliente")
        with st.form("new_client_form"):
            name = st.text_input("Nome Completo*")
            sex = st.radio("Sexo", ["Masculino", "Feminino"], horizontal=True)
            
            col1, col2 = st.columns(2)
            with col1:
                cpf = st.text_input("CPF")
            with col2:
                rg = st.text_input("RG")
            
            col3, col4 = st.columns(2)
            with col3:
                birth_date = st.date_input("Data de Nascimento", value=None, format="DD/MM/YYYY")
            with col4:
                email = st.text_input("E-mail")

            st.subheader("Contatos")
            
            phones_to_save = []
            
            # Slot 1
            c1, c2 = st.columns(2)
            with c1: p1 = st.text_input("Telefone Principal*")
            with c2: cp1 = st.text_input("Complemento Principal")
            phones_to_save.append({'number': p1, 'complement': cp1})
            
            # Slot 2
            c3, c4 = st.columns(2)
            with c3: p2 = st.text_input("Telefone Secundário (Opcional)")
            with c4: cp2 = st.text_input("Complemento Secundário")
            phones_to_save.append({'number': p2, 'complement': cp2})

            st.subheader("Endereço")
            col_addr1, col_addr2 = st.columns([3, 1])
            with col_addr1:
                address = st.text_input("Logradouro (Rua, Av.)")
            with col_addr2:
                address_number = st.text_input("Número")
            
            neighborhood = st.text_input("Bairro")

            notes = st.text_area("Observações")
            
            submitted = st.form_submit_button("Salvar Cliente")
            
            # Show success message right after button
            if 'show_save_success' in st.session_state and st.session_state.show_save_success:
                st.markdown('<p style="color: #22c55e; font-size: 0.9em; margin-top: 5px; font-weight: 500;">✓ Salvo com sucesso!</p>', unsafe_allow_html=True)
                st.session_state.show_save_success = False
            
            if submitted:
                if not name:
                    st.error("O campo Nome é obrigatório.")
                elif not p1:
                    st.error("O campo Telefone Principal é obrigatório.")
                else:
                    st.session_state.show_save_success = True
                    add_client(name, sex, phones_to_save, email, cpf, rg, birth_date, address, address_number, neighborhood, notes)

    with tab2:
        st.header("Clientes Cadastrados")
        
        # Search Bar
        search_term = st.text_input("Buscar", label_visibility="collapsed", placeholder="🔍 Pesquisar Cliente (Nome, Telefone, Email, CPF)")
        
        df = get_clients()
        
        # Filter Logic
        if not df.empty and search_term:
            # Prepare search columns, filling NaNs with empty string
            df_search = df.fillna("")
            df = df[
                df_search['name'].str.contains(search_term, case=False) |
                df_search['phone_display'].str.contains(search_term, case=False) |
                df_search['email'].str.contains(search_term, case=False) |
                df_search['cpf'].str.contains(search_term, case=False) |
                df_search['notes'].str.contains(search_term, case=False)
            ]

        if not df.empty:
            # Custom Layout: Row per Client
            for index, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 2])
                
                with col1:
                    # Name is now a button that opens the edit dialog
                    if st.button(f"**{row['name']}**", key=f"name_{row['id']}"):
                        if 'active_prescription_client' in st.session_state: del st.session_state.active_prescription_client
                        edit_client_dialog(row)
                    # Show small info below name
                    if row.get('cpf'):
                        st.caption(f"CPF: {row['cpf']}")
                with col2:
                    st.write(f"📞 {row['phone_display']}")
                with col3:
                    if st.button("Ordens de Serviço", key=f"os_{row['id']}"):
                        if 'active_prescription_client' in st.session_state: del st.session_state.active_prescription_client
                        pass # Placeholder
                with col4:
                    if st.button("Receitas", key=f"rec_{row['id']}"):
                        st.session_state.active_prescription_client = {'id': row['id'], 'name': row['name']}
                        st.session_state.new_prescription_expander_open = False # Always start closed
                        st.session_state.scroll_to_top = False # Ensure no scroll weirdness
                        st.rerun() # Force rerun to open dialog immediately via state check below
                with col5:
                    if st.button("Crediário", key=f"cred_{row['id']}"):
                         if 'active_prescription_client' in st.session_state: del st.session_state.active_prescription_client
                         pass # Placeholder
                
                st.divider()
        else:
            if search_term:
                st.warning("Nenhum cliente encontrado com esse termo.")
            else:
                st.info("Nenhum cliente cadastrado ainda.")

    # Check for active prescription dialog
    if 'active_prescription_client' in st.session_state:
        client_info = st.session_state.active_prescription_client
        # We invoke the dialog function. 
        # Note: Closing the dialog via "X" does NOT clear this state automatically.
        # But this ensures it survives 'st.rerun()' from inside the dialog.
        prescriptions.show_prescriptions_dialog(client_info['id'], client_info['name'])



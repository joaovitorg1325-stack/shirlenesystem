import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from modules.database import get_supabase

DB_FILE = "optical_store.db"  # kept for reference only

def init_db():
    """No longer needed - tables are created directly in Supabase."""
    pass

def add_professional_to_db(name):
    sb = get_supabase()
    try:
        sb.table('professionals').insert({'name': name}).execute()
    except Exception:
        st.warning(f"Profissional '{name}' já existe.")

def get_professionals():
    sb = get_supabase()
    res = sb.table('professionals').select('name').order('name').execute()
    return [r['name'] for r in res.data]

def get_all_professionals_detailed():
    """Get all professionals with their IDs"""
    sb = get_supabase()
    res = sb.table('professionals').select('id, name').order('name').execute()
    return pd.DataFrame(res.data)

def update_professional(prof_id, new_name):
    """Update a professional's name"""
    sb = get_supabase()
    try:
        sb.table('professionals').update({'name': new_name}).eq('id', prof_id).execute()
        st.success(f"Profissional atualizado para '{new_name}'!")
    except Exception:
        st.error(f"Já existe um profissional com o nome '{new_name}'.")

def delete_professional(prof_id):
    """Delete a professional"""
    sb = get_supabase()
    sb.table('professionals').delete().eq('id', prof_id).execute()
    st.success("Profissional excluído!")
    st.rerun()

def add_prescription(client_id, exam_date, expiration_date, professional, longe_data, addition, perto_data, notes):
    sb = get_supabase()
    date_str = exam_date.strftime('%Y-%m-%d') if exam_date else None
    exp_str = expiration_date.strftime('%Y-%m-%d') if expiration_date else None
    sb.table('prescriptions').insert({
        'client_id': client_id, 'exam_date': date_str, 'expiration_date': exp_str, 'professional': professional,
        'od_sph': longe_data['od_sph'], 'od_cyl': longe_data['od_cyl'], 'od_axis': longe_data['od_axis'],
        'od_dnp': longe_data['od_dnp'], 'od_height': longe_data['od_height'],
        'oe_sph': longe_data['oe_sph'], 'oe_cyl': longe_data['oe_cyl'], 'oe_axis': longe_data['oe_axis'],
        'oe_dnp': longe_data['oe_dnp'], 'oe_height': longe_data['oe_height'],
        'addition': addition,
        'od_perto_sph': perto_data['od_sph'], 'od_perto_cyl': perto_data['od_cyl'],
        'od_perto_axis': perto_data['od_axis'], 'od_perto_dnp': perto_data['od_dnp'],
        'oe_perto_sph': perto_data['oe_sph'], 'oe_perto_cyl': perto_data['oe_cyl'],
        'oe_perto_axis': perto_data['oe_axis'], 'oe_perto_dnp': perto_data['oe_dnp'],
        'notes': notes
    }).execute()
    st.rerun()

def update_prescription(prescription_id, client_id, exam_date, expiration_date, professional, longe_data, addition, perto_data, notes):
    sb = get_supabase()
    date_str = exam_date.strftime('%Y-%m-%d') if exam_date else None
    exp_str = expiration_date.strftime('%Y-%m-%d') if expiration_date else None
    sb.table('prescriptions').update({
        'client_id': client_id, 'exam_date': date_str, 'expiration_date': exp_str, 'professional': professional,
        'od_sph': longe_data['od_sph'], 'od_cyl': longe_data['od_cyl'], 'od_axis': longe_data['od_axis'],
        'od_dnp': longe_data['od_dnp'], 'od_height': longe_data['od_height'],
        'oe_sph': longe_data['oe_sph'], 'oe_cyl': longe_data['oe_cyl'], 'oe_axis': longe_data['oe_axis'],
        'oe_dnp': longe_data['oe_dnp'], 'oe_height': longe_data['oe_height'],
        'addition': addition,
        'od_perto_sph': perto_data['od_sph'], 'od_perto_cyl': perto_data['od_cyl'],
        'od_perto_axis': perto_data['od_axis'], 'od_perto_dnp': perto_data['od_dnp'],
        'oe_perto_sph': perto_data['oe_sph'], 'oe_perto_cyl': perto_data['oe_cyl'],
        'oe_perto_axis': perto_data['oe_axis'], 'oe_perto_dnp': perto_data['oe_dnp'],
        'notes': notes
    }).eq('id', prescription_id).execute()
    if 'editing_prescription_id' in st.session_state:
        del st.session_state['editing_prescription_id']
    st.rerun()

def get_prescriptions(client_id):
    sb = get_supabase()
    res = sb.table('prescriptions').select('*').eq('client_id', client_id).order('created_at', desc=True).execute()
    return pd.DataFrame(res.data)

def get_all_prescriptions():
    """Get all prescriptions from all clients with client names"""
    sb = get_supabase()
    res = sb.table('prescriptions').select('*, clients(name, store)').order('expiration_date').execute()
    df = pd.DataFrame(res.data)
    if not df.empty and 'clients' in df.columns:
        df['client_name'] = df['clients'].apply(lambda x: x['name'] if isinstance(x, dict) else '')
        df['store'] = df['clients'].apply(lambda x: x.get('store', '') if isinstance(x, dict) else '')
        df.drop(columns=['clients'], inplace=True)
    return df

def delete_prescription(id):
    sb = get_supabase()
    sb.table('prescriptions').delete().eq('id', id).execute()
    st.success("Receita excluída.")
    st.rerun()


def manage_professionals_ui():
    """UI to manage (edit/delete) professionals - shown inside prescriptions dialog"""
    st.markdown("### ⚙️ Gerenciar Profissionais")
    st.write("Gerencie os profissionais cadastrados no sistema.")
    
    # Back button
    if st.button("← Voltar para Receitas"):
        if 'show_manage_professionals' in st.session_state:
            del st.session_state.show_manage_professionals
        st.rerun()
    
    st.divider()
    
    df = get_all_professionals_detailed()
    
    if df.empty:
        st.info("Nenhum profissional cadastrado ainda.")
        return
    
    for index, row in df.iterrows():
        # Check if this professional is being edited
        is_editing = f'editing_prof_{row["id"]}' in st.session_state
        
        with st.container(border=True):
            if not is_editing:
                # VIEW MODE
                # Check if this professional is being deleted
                is_deleting = f'confirm_delete_prof_{row["id"]}' in st.session_state
                
                if not is_deleting:
                    col1, col2, col3 = st.columns([6, 1, 1])
                    col1.markdown(f"**👨‍⚕️ {row['name']}**")
                    
                    if col2.button("✏️", key=f"edit_prof_{row['id']}", help="Editar"):
                        st.session_state[f'editing_prof_{row["id"]}'] = True
                        st.session_state[f'prof_name_{row["id"]}'] = row['name']
                        st.rerun()
                    
                    if col3.button("🗑️", key=f"del_prof_{row['id']}", help="Excluir"):
                        st.session_state[f'confirm_delete_prof_{row["id"]}'] = True
                        st.rerun()
                else:
                    # Show confirmation
                    st.warning(f"⚠️ Tem certeza que deseja excluir **{row['name']}**?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Sim, excluir", key=f"confirm_yes_prof_{row['id']}", type="primary", use_container_width=True):
                            del st.session_state[f'confirm_delete_prof_{row["id"]}']
                            delete_professional(row['id'])
                    with col_no:
                        if st.button("❌ Cancelar", key=f"confirm_no_prof_{row['id']}", use_container_width=True):
                            del st.session_state[f'confirm_delete_prof_{row["id"]}']
                            st.rerun()

            else:
                # EDIT MODE
                st.markdown("**Editando Profissional:**")
                new_name = st.text_input(
                    "Nome",
                    value=st.session_state.get(f'prof_name_{row["id"]}', row['name']),
                    key=f"input_prof_{row['id']}"
                )
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Salvar", key=f"save_prof_{row['id']}", type="primary", use_container_width=True):
                        if new_name.strip():
                            update_professional(row['id'], new_name.strip())
                            del st.session_state[f'editing_prof_{row["id"]}']
                            del st.session_state[f'prof_name_{row["id"]}']
                            st.rerun()
                        else:
                            st.error("Nome não pode ser vazio!")
                
                with col_cancel:
                    if st.button("❌ Cancelar", key=f"cancel_prof_{row['id']}", use_container_width=True):
                        del st.session_state[f'editing_prof_{row["id"]}']
                        del st.session_state[f'prof_name_{row["id"]}']
                        st.rerun()

@st.dialog("Histórico de Receitas", width="large")
def show_prescriptions_dialog(client_id, client_name):
    init_db()
    
    # Check if we should show manage professionals UI
    if 'show_manage_professionals' in st.session_state and st.session_state.show_manage_professionals:
        manage_professionals_ui()
        return  # Exit early, don't show prescription form
    
    # Scroll to top if flag is set
    if 'scroll_to_top' in st.session_state and st.session_state.scroll_to_top:
        components.html("""
            <script>
                // Scroll the dialog to top
                setTimeout(function() {
                    const dialog = window.parent.document.querySelector('[data-testid="stDialog"]');
                    if (dialog) {
                        dialog.scrollTop = 0;
                    }
                }, 100);
            </script>
        """, height=0, width=0)
        # Clear the flag
        del st.session_state.scroll_to_top
    
    # JS Injection for Auto-Select + Dynamic Coloring + Input Filtering + Prevent Enter Submit
    components.html("""
        <script>
            function applyLogic() {
                const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                inputs.forEach(input => {
                    // Prevent Enter key submission
                    // CHANGE: Allow Enter on 'Nome do Novo Profissional' checking placeholder
                    if (input.placeholder && input.placeholder.includes('Digite o nome do profissional')) {
                         return; // Allow Enter
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
                    
                    // Check if target identifying aria-label
                    if (input.ariaLabel && (
                        input.ariaLabel.includes('Sph') || 
                        input.ariaLabel.includes('Cyl') || 
                        input.ariaLabel.includes('Adição') ||
                        input.ariaLabel.includes('Axis') ||
                        input.ariaLabel.includes('DNP') ||
                        input.ariaLabel.includes('Height')
                    )) {
                        // 1. Auto-Select on Focus
                        if (!input.dataset.autoSelectAttached) {
                            input.dataset.autoSelectAttached = "true";
                            input.addEventListener('focus', function() {
                                this.select();
                            });
                            
                            // Add input listener for color
                            input.addEventListener('input', function() {
                                updateColor(this);
                                // Filter invalid characters
                                filterInput(this);
                            });
                        }
                        
                        // 2. Dynamic Color (Run always)
                        updateColor(input);
                    }
                });
            }

            function filterInput(input) {
                // Only allow: numbers (0-9), plus (+), minus (-), and comma (,)
                const validPattern = /^[0-9+\-,]*$/;
                const currentValue = input.value;
                
                if (!validPattern.test(currentValue)) {
                    // Remove invalid characters
                    input.value = currentValue.replace(/[^0-9+\-,]/g, '');
                    // Trigger change event to update session state
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }

            function updateColor(input) {
                // Check if it's a Cylinder field
                const isCyl = input.ariaLabel && input.ariaLabel.includes('Cyl');
                const val = input.value;

                if (val.includes('-')) {
                    // Explicit Negative -> Red
                    input.style.color = '#d32f2f'; 
                    input.style.webkitTextFillColor = '#d32f2f';
                } else if (val.includes('+')) {
                    // Explicit Positive -> Green
                    input.style.color = '#2e7d32'; 
                    input.style.webkitTextFillColor = '#2e7d32';
                } else {
                    // No Sign present (e.g. "200", "0,00", "")
                    if (isCyl) {
                        // Cylinder defaults to Red (anticipating negative)
                        input.style.color = '#d32f2f'; 
                        input.style.webkitTextFillColor = '#d32f2f';
                    } else {
                        // Others (Sph, Add) default to Green
                        input.style.color = '#2e7d32'; 
                        input.style.webkitTextFillColor = '#2e7d32';
                    }
                }
                input.style.fontWeight = 'bold';
            }

            // Run on load
            applyLogic();

            // Run heavily on intervals to catch re-renders
            setInterval(applyLogic, 500); 
        </script>
    """, height=0, width=0)
    
    # Initialize Session State with "0,00" defaults
    keys_to_init = [
        "od_sph", "od_cyl", "od_axis", "od_dnp", "od_height", 
        "oe_sph", "oe_cyl", "oe_axis", "oe_dnp", "oe_height",
        "addition",
        "od_p_sph", "od_p_cyl", "od_p_axis", "od_p_dnp",
        "oe_p_sph", "oe_p_cyl", "oe_p_axis", "oe_p_dnp"
    ]
    for key in keys_to_init:
        if key not in st.session_state:
            # Axis, DNP, Height maybe shouldn't be 0,00? 
            # User said "os campos" (plural, generic). 
            # But "0,00" for Axis (0 to 180 int) is weird.
            # "0,00" for DNP (mm) is weird.
            # I will set "0,00" ONLY for Dioptria fields (Sph, Cyl, Add).
            # Others empty or "0"? User said "Deixe os Campos já pré preenchidos com o número 00,00".
            # I will apply to Sph, Cyl, Add.
            if "sph" in key or "cyl" in key or "addition" in key:
                st.session_state[key] = "0,00"
            else:
                st.session_state[key] = "" # Keep others empty
    
    # Check if we need to load data for editing (BEFORE widgets are created)
    # NOTE: This is no longer used since we moved to inline editing, but keeping initialization
    is_editing = False  # Always false now since inline editing handles this
    
    # --- Edit Mode Automation Callback ---
    def update_edit_dioptria(key, row_id, field_name, is_cyl=False):
        """Callback to handle formatting and auto-calculation in edit mode."""
        if key not in st.session_state: return
        
        val = st.session_state[key]
        
        # 1. Format Logic (Comma, Decimals)
        if val:
            val_clean = val.strip().replace(",", ".")
            if "." not in val_clean:
                try:
                    # Integer input logic
                    float_val = float(val_clean)
                    # Heuristic: < 25 -> whole diopters (2 -> 2.00), >= 25 -> cent-diopters (200 -> 2.00)
                    if abs(float_val) >= 25:
                        float_val = float_val / 100.0
                    val = "{:.2f}".format(float_val).replace(".", ",")
                except ValueError:
                    pass 
            else:
                try:
                    # Float input -> ensure 2 decimals
                    float_val = float(val_clean)
                    val = "{:.2f}".format(float_val).replace(".", ",")
                except ValueError:
                    pass

            # 2. Cyl Negative Logic (if Is Cyl)
            # Force negative only if NO SIGN is present
            if is_cyl and val != "0,00" and val != "-0,00":
                if not val.startswith('-') and not val.startswith('+'):
                     val = "-" + val
        
        # Update Widget Value
        st.session_state[key] = val
        
        # Update Data Dictionary
        edit_data = st.session_state.get(f'edit_data_{row_id}', {})
        edit_data[field_name] = val
        st.session_state[f'edit_data_{row_id}'] = edit_data
        
        # 3. Auto-Calculate NEAR (if triggered by Longe Sph/Cyl or Addition)
        triggers = ["od_sph", "oe_sph", "od_cyl", "oe_cyl", "addition"]
        if field_name in triggers:
            def parse_float_local(v):
                if not v: return 0.0
                try: return float(str(v).replace(",", "."))
                except: return 0.0

            add_val = parse_float_local(edit_data.get('addition', '0,00'))
            
            # Helper to update specific eye near
            def update_edit_eye_near(prefix):
                # Sph: Longe + Add
                l_sph = edit_data.get(f'{prefix}_sph', '')
                if l_sph:
                    l_val = parse_float_local(l_sph)
                    p_val = l_val + add_val
                    
                    # Format back
                    p_str = "{:.2f}".format(p_val).replace(".", ",")
                    
                    # Ensure sign
                    if not p_str.startswith("-") and not p_str.startswith("+") and p_val != 0:
                        p_str = "+" + p_str
                    
                    # Update Near Sph in Data & Widget
                    edit_data[f'{prefix}_perto_sph'] = p_str
                    # Also update widget key if it exists: e_{prefix}_p_sph_{row_id}
                    st.session_state[f"e_{prefix}_p_sph_{row_id}"] = p_str
                
                # Cyl: Copy Longe -> Near
                l_cyl = edit_data.get(f'{prefix}_cyl', '')
                edit_data[f'{prefix}_perto_cyl'] = l_cyl
                st.session_state[f"e_{prefix}_p_cyl_{row_id}"] = l_cyl

            update_edit_eye_near("od")
            update_edit_eye_near("oe")
            
            # Save back updated edit_data
            st.session_state[f'edit_data_{row_id}'] = edit_data

    
    # Control expander state
    if 'new_prescription_expander_open' not in st.session_state:
        st.session_state.new_prescription_expander_open = False
    
    # Add New Prescription Form
    form_title = "➕ Nova Receita"
    
    with st.expander(form_title, expanded=st.session_state.new_prescription_expander_open):
        # Prevent auto-closing on interaction
        def keep_open():
            st.session_state.new_prescription_expander_open = True
        
        # Professional Logic
        profs = get_professionals()
        if 'new_prof_mode' not in st.session_state:
             st.session_state.new_prof_mode = False

        c_prof1, c_prof2 = st.columns([3, 1])
        with c_prof1:
            if not st.session_state.new_prof_mode:
                # Always use selectbox
                options = profs + ["➕ Cadastrar Novo...", "⚙️ Gerenciar Profissionais"]
                
                # Set default professional
                default_prof_idx = 0
                
                # Check if we have a newly created professional to select
                if 'selected_professional' in st.session_state:
                    if st.session_state.selected_professional in options:
                        default_prof_idx = options.index(st.session_state.selected_professional)
                    # Clear it after using
                    del st.session_state.selected_professional
                elif is_editing and 'prof_select' not in st.session_state:
                     # Try to find current prof in options to set index
                     current_prof = st.session_state.get('editing_prescription_data', {}).get('professional', '')
                     if current_prof in options:
                         default_prof_idx = options.index(current_prof)
                
                professional = st.selectbox("Profissional", options=options, index=default_prof_idx, key="prof_select", on_change=keep_open)
                
                if professional == "➕ Cadastrar Novo...":
                    st.session_state.new_prof_mode = True
                    st.rerun()
                elif professional == "⚙️ Gerenciar Profissionais":
                    st.session_state.show_manage_professionals = True
                    st.rerun()
            else:
                 def save_new_prof_callback():
                     name = st.session_state.new_prof_name_input
                     if name:
                         add_professional_to_db(name)
                         # Store the newly created professional to auto-select it
                         st.session_state.selected_professional = name
                         st.session_state.new_prof_mode = False
                         # Input on_change already triggers rerun, so explicit rerun is not needed/allowed here.



                 new_prof_name = st.text_input("Nome do Novo Profissional", key="new_prof_name_input", on_change=save_new_prof_callback, placeholder="Digite o nome do profissional")
                 
                 if st.button("Salvar Profissional"):
                     if new_prof_name:
                         add_professional_to_db(new_prof_name)
                         # Store the newly created professional to auto-select it
                         st.session_state.selected_professional = new_prof_name
                         st.session_state.new_prof_mode = False
                         st.rerun()
                 if st.button("Cancelar"):
                     st.session_state.new_prof_mode = False
                     st.rerun()
                 professional = new_prof_name 

        c1, c2 = st.columns(2)
        with c1:
            # Date defaults
            default_date = datetime.today()
            if is_editing:
                try:
                    date_str = st.session_state.get('editing_prescription_data', {}).get('exam_date')
                    if date_str: default_date = datetime.strptime(date_str, '%Y-%m-%d')
                except: pass
            
            exam_date = st.date_input("Data do Exame", value=default_date, format="DD/MM/YYYY", key="exam_date_input", on_change=keep_open)
        with c2:
            # Auto-calc validade
            default_exp = exam_date + timedelta(days=365)
            if is_editing:
                 try:
                    exp_str = st.session_state.get('editing_prescription_data', {}).get('expiration_date')
                    if exp_str: default_exp = datetime.strptime(exp_str, '%Y-%m-%d')
                 except: pass
            
            expiration_date = st.date_input("Validade (Vencimento)", value=default_exp, format="DD/MM/YYYY", key="exp_date_input", on_change=keep_open)

        st.divider()
        
        # --- Realtime Formatting Callback (Updated for Comma) ---
        def update_dioptria(key, is_cyl=False):
            st.session_state.new_prescription_expander_open = True
            val = st.session_state[key]
            if not val: return
            
            # Format logic: 200 -> 2,00
            val_clean = val.strip().replace(",", ".") # working with dot internally for float conversion
            
            # Check if it was "0,00" (default) being edited?
            # If user types over it, it's fine.
            
            if "." not in val_clean:
                try:
                    # Integer input logic
                    float_val = float(val_clean)
                    
                    # Smart Heuristic:
                    # If |val| < 25, assume user meant whole diopters (e.g. 2 -> 2.00, 10 -> 10.00).
                    # If |val| >= 25, assume cent-diopters (e.g. 75 -> 0.75, 200 -> 2.00).
                    # This avoids 2 becoming 0.02, while keeping 75 as 0.75.
                    if abs(float_val) >= 25:
                        float_val = float_val / 100.0
                    
                    # Output with COMMA
                    val = "{:.2f}".format(float_val).replace(".", ",")
                except ValueError:
                    pass 
            else:
                try:
                    # Float input -> ensure 2 decimals
                    float_val = float(val_clean)
                    val = "{:.2f}".format(float_val).replace(".", ",")
                except ValueError:
                    pass

            # 2. Cyl Negative Logic
            if is_cyl:
                # Force negative only if NO SIGN is present
                # val is like "2,00" or "-2,00" or "+2,00"
                if val != "0,00" and val != "-0,00":
                    if not val.startswith('-') and not val.startswith('+'):
                         val = "-" + val
            
            st.session_state[key] = val

            # --- 3. Auto-Calculate PERTO (Near) ---
            # Rules:
            # - Trigger: Change in Longe (Sph/Cyl) or Addition
            # - Perto Sph = Longe Sph + Addition
            # - Perto Cyl = Longe Cyl (Copy)
            # - Ignore Axis/Height/DNP
            
            # Identify determining fields
            triggers = ["od_sph", "oe_sph", "od_cyl", "oe_cyl", "addition"]
            
            if key in triggers:
                def parse_float(v):
                    if not v: return 0.0
                    try:
                        return float(v.replace(",", "."))
                    except:
                        return 0.0

                adicao_val = parse_float(st.session_state.get("addition", "0,00"))
                
                # Helper to update specific eye
                def update_eye_near(eye_prefix):
                    # 1. Sphere Calculation
                    l_sph = st.session_state.get(f"{eye_prefix}_sph", "")
                    if l_sph: # Only if Longe is set
                        l_sph_val = parse_float(l_sph)
                        p_sph_val = l_sph_val + adicao_val
                        
                        # Format back
                        p_sph_str = "{:.2f}".format(p_sph_val).replace(".", ",")
                        # Add sign if positive/zero and not present? 
                        # Usually dioptria has sign.
                        if p_sph_val > 0: p_sph_str = "+" + p_sph_str
                         # If it was 0, maybe just "0,00"? or "+0,00"? Standard is usually just 0,00 or +0,00. 
                         # Let's stick to standard formatting safely.
                        
                        # Update Session State for Perto Sph
                        st.session_state[f"{eye_prefix}_p_sph"] = p_sph_str
                    
                    # 2. Cylinder Copy
                    l_cyl = st.session_state.get(f"{eye_prefix}_cyl", "")
                    if l_cyl:
                        st.session_state[f"{eye_prefix}_p_cyl"] = l_cyl

                # Execute update
                if "od" in key or key == "addition":
                    update_eye_near("od")
                if "oe" in key or key == "addition":
                    update_eye_near("oe")
        
        # --- Auto-fill Height Callback ---
        def auto_fill_height():
            st.session_state.new_prescription_expander_open = True
            # Only trigger on first fill of a new prescription
            if 'height_auto_filled' not in st.session_state:
                od_h = st.session_state.get('od_height', '')
                if od_h and od_h.strip():  # If OD Height has a value
                    st.session_state['oe_height'] = od_h
                    st.session_state['height_auto_filled'] = True

        # --- LONGE ---
        st.markdown("##### 🌅 Longe")
        
        # Matrix Headers
        cols_l = st.columns([0.5, 1, 1, 1, 1, 1])
        cols_l[0].write("")
        cols_l[1].write("Esférico")
        cols_l[2].write("Cilíndrico") 
        cols_l[3].write("Eixo")
        cols_l[4].write("DNP")
        cols_l[5].write("Altura")
        
        # OD Longe
        c_od_l = st.columns([0.5, 1, 1, 1, 1, 1])
        c_od_l[0].markdown("**OD**")
        od_sph = c_od_l[1].text_input("OD Sph", key="od_sph", label_visibility="collapsed", on_change=update_dioptria, args=("od_sph",))
        od_cyl = c_od_l[2].text_input("OD Cyl", key="od_cyl", label_visibility="collapsed", on_change=update_dioptria, args=("od_cyl", True))
        od_axis = c_od_l[3].text_input("OD Axis", key="od_axis", label_visibility="collapsed", on_change=keep_open)
        od_dnp = c_od_l[4].text_input("OD DNP", key="od_dnp", label_visibility="collapsed", on_change=keep_open)
        od_height = c_od_l[5].text_input("OD Height", key="od_height", label_visibility="collapsed", on_change=auto_fill_height)
        
        # OE Longe
        c_oe_l = st.columns([0.5, 1, 1, 1, 1, 1])
        c_oe_l[0].markdown("**OE**")
        oe_sph = c_oe_l[1].text_input("OE Sph", key="oe_sph", label_visibility="collapsed", on_change=update_dioptria, args=("oe_sph",))
        oe_cyl = c_oe_l[2].text_input("OE Cyl", key="oe_cyl", label_visibility="collapsed", on_change=update_dioptria, args=("oe_cyl", True))
        oe_axis = c_oe_l[3].text_input("OE Axis", key="oe_axis", label_visibility="collapsed", on_change=keep_open)
        oe_dnp = c_oe_l[4].text_input("OE DNP", key="oe_dnp", label_visibility="collapsed", on_change=keep_open)
        oe_height = c_oe_l[5].text_input("OE Height", key="oe_height", label_visibility="collapsed", on_change=keep_open)

        st.write("") # Spacer

        # --- ADIÇÃO ---
        c_add1, c_add2, c_add3 = st.columns([1, 1, 3])
        with c_add1:
            st.markdown("##### ➕ Adição")
        with c_add2:
            addition = st.text_input("Adição", key="addition", label_visibility="collapsed", placeholder="+0,00", on_change=update_dioptria, args=("addition",))
        
        st.write("") # Spacer

        # --- PERTO ---
        st.markdown("##### 📖 Perto")
        cols_p = st.columns([0.5, 1, 1, 1, 1, 1])
        cols_p[0].write("")
        cols_p[1].write("Esférico")
        cols_p[2].write("Cilíndrico")
        cols_p[3].write("Eixo")
        cols_p[4].write("DNP")
        cols_p[5].write("") 
        
        # OD Perto
        c_od_p = st.columns([0.5, 1, 1, 1, 1, 1])
        c_od_p[0].markdown("**OD**")
        od_p_sph = c_od_p[1].text_input("OD Perto Sph", key="od_p_sph", label_visibility="collapsed", on_change=update_dioptria, args=("od_p_sph",))
        od_p_cyl = c_od_p[2].text_input("OD Perto Cyl", key="od_p_cyl", label_visibility="collapsed", on_change=update_dioptria, args=("od_p_cyl", True))
        od_p_axis = c_od_p[3].text_input("OD Perto Axis", key="od_p_axis", label_visibility="collapsed", on_change=keep_open)
        od_p_dnp = c_od_p[4].text_input("OD Perto DNP", key="od_p_dnp", label_visibility="collapsed", on_change=keep_open)
        
        # OE Perto
        c_oe_p = st.columns([0.5, 1, 1, 1, 1, 1])
        c_oe_p[0].markdown("**OE**")
        oe_p_sph = c_oe_p[1].text_input("OE Perto Sph", key="oe_p_sph", label_visibility="collapsed", on_change=update_dioptria, args=("oe_p_sph",))
        oe_p_cyl = c_oe_p[2].text_input("OE Perto Cyl", key="oe_p_cyl", label_visibility="collapsed", on_change=update_dioptria, args=("oe_p_cyl", True))
        oe_p_axis = c_oe_p[3].text_input("OE Perto Axis", key="oe_p_axis", label_visibility="collapsed", on_change=keep_open)
        oe_p_dnp = c_oe_p[4].text_input("OE Perto DNP", key="oe_p_dnp", label_visibility="collapsed", on_change=keep_open)
        
        st.divider()
        notes = st.text_area("Observações", key="notes_area", on_change=keep_open)
        
        if st.button("Salvar Receita" if not is_editing else "Atualizar Receita", type="primary"):
            # Auto-copy logic (on Save)
            if od_height and not oe_height: oe_height = od_height
            
            longe_data = {
                'od_sph': od_sph, 'od_cyl': od_cyl, 'od_axis': od_axis, 'od_dnp': od_dnp, 'od_height': od_height,
                'oe_sph': oe_sph, 'oe_cyl': oe_cyl, 'oe_axis': oe_axis, 'oe_dnp': oe_dnp, 'oe_height': oe_height
            }
            perto_data = {
                'od_sph': od_p_sph, 'od_cyl': od_p_cyl, 'od_axis': od_p_axis, 'od_dnp': od_p_dnp,
                'oe_sph': oe_p_sph, 'oe_cyl': oe_p_cyl, 'oe_axis': oe_p_axis, 'oe_dnp': oe_p_dnp
            }
            
            # Professional Check
            prof_final = str(professional) 
            
            if is_editing:
                update_prescription(st.session_state.editing_prescription_id, client_id, exam_date, expiration_date, prof_final, longe_data, addition, perto_data, notes)
            else:
                # Close the expander when saving new prescription
                st.session_state.new_prescription_expander_open = False
                
                # Set flag to scroll to top after rerun
                st.session_state.scroll_to_top = True
                
                # Clear all form fields before adding (so expander closes and fields reset on rerun)
                keys_to_clear = [
                    "od_sph", "od_cyl", "od_axis", "od_dnp", "od_height", 
                    "oe_sph", "oe_cyl", "oe_axis", "oe_dnp", "oe_height",
                    "addition",
                    "od_p_sph", "od_p_cyl", "od_p_axis", "od_p_dnp",
                    "oe_p_sph", "oe_p_cyl", "oe_p_axis", "oe_p_dnp",
                    "notes_area", "height_auto_filled"
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                add_prescription(client_id, exam_date, expiration_date, prof_final, longe_data, addition, perto_data, notes)

    st.divider()
    
    # List Existing Prescriptions (Styling!)
    df = get_prescriptions(client_id)
    if not df.empty:
        for index, row in df.iterrows():
            date_fmt = row['exam_date']
            exp_fmt = row['expiration_date']
            try:
                date_fmt = datetime.strptime(row['exam_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
                exp_fmt = datetime.strptime(row['expiration_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                pass
            
            # Check if this card is in edit mode
            is_editing_this = f'editing_inline_{row["id"]}' in st.session_state
            
            # Apply highlighted border CSS if in edit mode
            border_style = "border: 2px solid #4CAF50; box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);" if is_editing_this else ""
            
            with st.container(border=True):
                # Add custom CSS for this card if editing
                if is_editing_this:
                    st.markdown(f"""
                    <style>
                        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] input[type="text"] {{
                            border: 1px solid #4CAF50 !important;
                            box-shadow: 0 0 5px rgba(76, 175, 80, 0.2);
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                
                c_head1, c_head2, c_head3 = st.columns([10, 1, 1])
                c_head1.markdown(f"📅 **{date_fmt}** | Vence em: **{exp_fmt}** | 👨‍⚕️ {row['professional']}")
                
               # Edit/Save/Cancel buttons
                if not is_editing_this:
                    if c_head2.button("✏️", key=f"edit_{row['id']}", help="Editar Receita"):
                        # Enter inline edit mode
                        st.session_state[f'editing_inline_{row["id"]}'] = True
                        # Store original data
                        st.session_state[f'edit_data_{row["id"]}'] = row.to_dict()
                        st.rerun()
                else:
                    # Show Save and Cancel buttons
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Salvar", key=f"save_{row['id']}", type="primary", use_container_width=True):
                            # Get edited data from session_state
                            edit_data = st.session_state.get(f'edit_data_{row["id"]}', {})
                            
                            longe_data = {
                                'od_sph': edit_data.get('od_sph', ''),
                                'od_cyl': edit_data.get('od_cyl', ''),
                                'od_axis': edit_data.get('od_axis', ''),
                                'od_dnp': edit_data.get('od_dnp', ''),
                                'od_height': edit_data.get('od_height', ''),
                                'oe_sph': edit_data.get('oe_sph', ''),
                                'oe_cyl': edit_data.get('oe_cyl', ''),
                                'oe_axis': edit_data.get('oe_axis', ''),
                                'oe_dnp': edit_data.get('oe_dnp', ''),
                                'oe_height': edit_data.get('oe_height', '')
                            }
                            perto_data = {
                                'od_sph': edit_data.get('od_perto_sph', ''),
                                'od_cyl': edit_data.get('od_perto_cyl', ''),
                                'od_axis': edit_data.get('od_perto_axis', ''),
                                'od_dnp': edit_data.get('od_perto_dnp', ''),
                                'oe_sph': edit_data.get('oe_perto_sph', ''),
                                'oe_cyl': edit_data.get('oe_perto_cyl', ''),
                                'oe_axis': edit_data.get('oe_perto_axis', ''),
                                'oe_dnp': edit_data.get('oe_perto_dnp', '')
                            }
                            
                            try:
                                exam_date_obj = datetime.strptime(edit_data.get('exam_date', row['exam_date']), '%Y-%m-%d')
                                exp_date_obj = datetime.strptime(edit_data.get('expiration_date', row['expiration_date']), '%Y-%m-%d')
                            except:
                                exam_date_obj = datetime.today()
                                exp_date_obj = datetime.today()
                            
                            # Clear edit state BEFORE calling update (which does st.rerun)
                            del st.session_state[f'editing_inline_{row["id"]}']
                            del st.session_state[f'edit_data_{row["id"]}']
                            
                            update_prescription(
                                row['id'],
                                client_id,
                                exam_date_obj,
                                exp_date_obj,
                                edit_data.get('professional', row['professional']),
                                longe_data,
                                edit_data.get('addition', ''),
                                perto_data,
                                edit_data.get('notes', '')
                            )

                    
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_{row['id']}", use_container_width=True):
                            # Exit edit mode without saving
                            del st.session_state[f'editing_inline_{row["id"]}']
                            del st.session_state[f'edit_data_{row["id"]}']
                            st.rerun()
                
                # Delete Confirmation Popover (only show when not editing)
                if not is_editing_this:
                    with c_head3.popover("🗑️"):
                        st.write("Tem certeza?")
                        if st.button("Sim, excluir", key=f"del_confirm_{row['id']}"):
                            delete_prescription(row['id'])

                # Display/Edit Content
                if is_editing_this:
                    # EDIT MODE - Show input fields
                    edit_data = st.session_state.get(f'edit_data_{row["id"]}', row.to_dict())
                    
                    st.markdown("##### 🌅 Longe")
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    col1.write("**OD**")
                    
                    k_od_sph = f"e_od_sph_{row['id']}"
                    edit_data['od_sph'] = col2.text_input("OD Sph", value=str(edit_data.get('od_sph', '')), key=k_od_sph, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_sph, row['id'], 'od_sph', False))
                    
                    k_od_cyl = f"e_od_cyl_{row['id']}"
                    edit_data['od_cyl'] = col3.text_input("OD Cyl", value=str(edit_data.get('od_cyl', '')), key=k_od_cyl, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_cyl, row['id'], 'od_cyl', True))
                    
                    k_od_axis = f"e_od_axis_{row['id']}"
                    edit_data['od_axis'] = col4.text_input("OD Axis", value=str(edit_data.get('od_axis', '')), key=k_od_axis, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_axis, row['id'], 'od_axis', False))
                    
                    k_od_dnp = f"e_od_dnp_{row['id']}"
                    edit_data['od_dnp'] = col5.text_input("OD DNP", value=str(edit_data.get('od_dnp', '')), key=k_od_dnp, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_dnp, row['id'], 'od_dnp', False))
                    
                    k_od_height = f"e_od_height_{row['id']}"
                    edit_data['od_height'] = col6.text_input("OD Height", value=str(edit_data.get('od_height', '')), key=k_od_height, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_height, row['id'], 'od_height', False))
                    
                    col1b, col2b, col3b, col4b, col5b, col6b = st.columns(6)
                    col1b.write("**OE**")
                    
                    k_oe_sph = f"e_oe_sph_{row['id']}"
                    edit_data['oe_sph'] = col2b.text_input("OE Sph", value=str(edit_data.get('oe_sph', '')), key=k_oe_sph, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_sph, row['id'], 'oe_sph', False))
                    
                    k_oe_cyl = f"e_oe_cyl_{row['id']}"
                    edit_data['oe_cyl'] = col3b.text_input("OE Cyl", value=str(edit_data.get('oe_cyl', '')), key=k_oe_cyl, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_cyl, row['id'], 'oe_cyl', True))
                    
                    k_oe_axis = f"e_oe_axis_{row['id']}"
                    edit_data['oe_axis'] = col4b.text_input("OE Axis", value=str(edit_data.get('oe_axis', '')), key=k_oe_axis, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_axis, row['id'], 'oe_axis', False))
                    
                    k_oe_dnp = f"e_oe_dnp_{row['id']}"
                    edit_data['oe_dnp'] = col5b.text_input("OE DNP", value=str(edit_data.get('oe_dnp', '')), key=k_oe_dnp, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_dnp, row['id'], 'oe_dnp', False))
                    
                    k_oe_height = f"e_oe_height_{row['id']}"
                    edit_data['oe_height'] = col6b.text_input("OE Height", value=str(edit_data.get('oe_height', '')), key=k_oe_height, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_height, row['id'], 'oe_height', False))
                    
                    st.markdown("##### ➕ Adição")
                    k_add = f"e_addition_{row['id']}"
                    edit_data['addition'] = st.text_input("Adição", value=str(edit_data.get('addition', '')), key=k_add, on_change=update_edit_dioptria, args=(k_add, row['id'], 'addition', False))
                    
                    st.markdown("##### 📖 Perto")
                    col1c, col2c, col3c, col4c, col5c = st.columns(5)
                    col1c.write("**OD**")
                    
                    k_od_p_sph = f"e_od_p_sph_{row['id']}"
                    edit_data['od_perto_sph'] = col2c.text_input("OD P Sph", value=str(edit_data.get('od_perto_sph', '')), key=k_od_p_sph, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_p_sph, row['id'], 'od_perto_sph', False))
                    
                    k_od_p_cyl = f"e_od_p_cyl_{row['id']}"
                    edit_data['od_perto_cyl'] = col3c.text_input("OD P Cyl", value=str(edit_data.get('od_perto_cyl', '')), key=k_od_p_cyl, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_p_cyl, row['id'], 'od_perto_cyl', True))
                    
                    k_od_p_axis = f"e_od_p_axis_{row['id']}"
                    edit_data['od_perto_axis'] = col4c.text_input("OD P Axis", value=str(edit_data.get('od_perto_axis', '')), key=k_od_p_axis, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_p_axis, row['id'], 'od_perto_axis', False))
                    
                    k_od_p_dnp = f"e_od_p_dnp_{row['id']}"
                    edit_data['od_perto_dnp'] = col5c.text_input("OD P DNP", value=str(edit_data.get('od_perto_dnp', '')), key=k_od_p_dnp, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_od_p_dnp, row['id'], 'od_perto_dnp', False))
                    
                    col1d, col2d, col3d, col4d, col5d = st.columns(5)
                    col1d.write("**OE**")
                    
                    k_oe_p_sph = f"e_oe_p_sph_{row['id']}"
                    edit_data['oe_perto_sph'] = col2d.text_input("OE P Sph", value=str(edit_data.get('oe_perto_sph', '')), key=k_oe_p_sph, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_p_sph, row['id'], 'oe_perto_sph', False))
                    
                    k_oe_p_cyl = f"e_oe_p_cyl_{row['id']}"
                    edit_data['oe_perto_cyl'] = col3d.text_input("OE P Cyl", value=str(edit_data.get('oe_perto_cyl', '')), key=k_oe_p_cyl, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_p_cyl, row['id'], 'oe_perto_cyl', True))
                    
                    k_oe_p_axis = f"e_oe_p_axis_{row['id']}"
                    edit_data['oe_perto_axis'] = col4d.text_input("OE P Axis", value=str(edit_data.get('oe_perto_axis', '')), key=k_oe_p_axis, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_p_axis, row['id'], 'oe_perto_axis', False))
                    
                    k_oe_p_dnp = f"e_oe_p_dnp_{row['id']}"
                    edit_data['oe_perto_dnp'] = col5d.text_input("OE P DNP", value=str(edit_data.get('oe_perto_dnp', '')), key=k_oe_p_dnp, label_visibility="collapsed", on_change=update_edit_dioptria, args=(k_oe_p_dnp, row['id'], 'oe_perto_dnp', False))
                    
                    edit_data['notes'] = st.text_area("Observações", value=str(edit_data.get('notes', '')), key=f"e_notes_{row['id']}")
                    
                    # Update session state
                    st.session_state[f'edit_data_{row["id"]}'] = edit_data
                    
                else:
                    # VIEW MODE - Show formatted display
                    def fmt_val(val, is_cyl=False):
                        if not val: return "-"
                        val = str(val).strip().replace(".", ",") # Ensure comma for display
                        color = "black"
                        if val.startswith('+') or (not val.startswith('-') and val != "0" and val != "0,00" and not is_cyl):
                            color = "green"
                        elif val.startswith('-') or is_cyl:
                            color = "red"
                        return f"<span style='color:{color};'>{val}</span>"

                    # Display Values (Compact Table with Color)
                    st.markdown(f"""
                    <div style="font-size: 0.9em;">
                        <strong>Longe</strong>
                        <table style="width:100%; text-align: center;">
                            <thead style="border-bottom: 1px solid #ddd;">
                                <tr><th>Olho</th><th>Esférico</th><th>Cilíndrico</th><th>Eixo</th><th>DNP</th><th>Altura</th></tr>
                            </thead>
                            <tbody>
                                <tr><td><b>OD</b></td><td>{fmt_val(row['od_sph'])}</td><td>{fmt_val(row['od_cyl'], True)}</td><td>{row['od_axis']}</td><td>{row['od_dnp']}</td><td>{row['od_height']}</td></tr>
                                <tr><td><b>OE</b></td><td>{fmt_val(row['oe_sph'])}</td><td>{fmt_val(row['oe_cyl'], True)}</td><td>{row['oe_axis']}</td><td>{row['oe_dnp']}</td><td>{row['oe_height']}</td></tr>
                            </tbody>
                        </table>
                        <div style="margin: 10px 0; text-align: center;">
                            <b>Adição:</b> {fmt_val(row['addition'])}
                        </div>
                        <strong>Perto</strong>
                        <table style="width:100%; text-align: center;">
                             <thead style="border-bottom: 1px solid #ddd;">
                                <tr><th>Olho</th><th>Esférico</th><th>Cilíndrico</th><th>Eixo</th><th>DNP</th><th>-</th></tr>
                            </thead>
                            <tbody>
                                <tr><td><b>OD</b></td><td>{fmt_val(row['od_perto_sph'])}</td><td>{fmt_val(row['od_perto_cyl'], True)}</td><td>{row['od_perto_axis']}</td><td>{row['od_perto_dnp']}</td><td>-</td></tr>
                                <tr><td><b>OE</b></td><td>{fmt_val(row['oe_perto_sph'])}</td><td>{fmt_val(row['oe_perto_cyl'], True)}</td><td>{row['oe_perto_axis']}</td><td>{row['oe_perto_dnp']}</td><td>-</td></tr>
                            </tbody>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if row['notes']:
                        st.caption(f"📝{row['notes']}")
    else:
        st.info("Nenhuma receita cadastrada para este cliente.")

def show():
    """Global Prescriptions List Page"""
    init_db()
    
    st.title("📋 Receitas")
    st.write("Lista de todas as receitas cadastradas no sistema")
    
    # Search and Filter Controls
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("🔍 Buscar por nome do cliente", placeholder="Digite o nome...")
    
    with col2:
        sort_option = st.selectbox(
            "Ordenar por",
            ["Vencimento (Mais próximo)", "Vencimento (Mais distante)", "Data do Exame", "Nome do Cliente"]
        )
    
    # Get all prescriptions
    df = get_all_prescriptions()
    
    if df.empty:
        st.info("Nenhuma receita cadastrada no sistema.")
        return
    
    # Apply search filter
    if search_term:
        df = df[df['client_name'].str.contains(search_term, case=False, na=False)]
    
    # Apply sorting
    if sort_option == "Vencimento (Mais próximo)":
        df = df.sort_values('expiration_date', ascending=True)
    elif sort_option == "Vencimento (Mais distante)":
        df = df.sort_values('expiration_date', ascending=False)
    elif sort_option == "Data do Exame":
        df = df.sort_values('exam_date', ascending=False)
    elif sort_option == "Nome do Cliente":
        df = df.sort_values('client_name', ascending=True)
    
    # Display results count
    st.caption(f"Mostrando {len(df)} receita(s)")
    
    # Display prescriptions
    if not df.empty:
        for index, row in df.iterrows():
            # Format dates
            date_fmt = row['exam_date']
            exp_fmt = row['expiration_date']
            try:
                exam_date_obj = datetime.strptime(row['exam_date'], '%Y-%m-%d')
                exp_date_obj = datetime.strptime(row['expiration_date'], '%Y-%m-%d')
                date_fmt = exam_date_obj.strftime('%d/%m/%Y')
                exp_fmt = exp_date_obj.strftime('%d/%m/%Y')
                
                # Check if expired
                is_expired = exp_date_obj < datetime.now()
                exp_color = "🔴" if is_expired else "🟢"
            except:
                is_expired = False
                exp_color = "⚪"
            
            with st.container(border=True):
                # Header with client name and dates
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.markdown(f"### 👤 {row['client_name']}")
                    st.markdown(f"📅 **Exame:** {date_fmt} | {exp_color} **Vence:** {exp_fmt} | 👨‍⚕️ {row['professional']}")
                
                with col_b:
                    if st.button("Ver Cliente", key=f"view_client_{row['id']}", use_container_width=True):
                        # Navigate to client page (would open clients page with this client)
                        st.info(f"Navegue para a página de Clientes e procure por: {row['client_name']}")
                
                # Prescription details in expander
                with st.expander("Ver Detalhes da Receita"):
                    # Helper for color
                    def fmt_val(val, is_cyl=False):
                        if not val: return "-"
                        val = str(val).strip().replace(".", ",")
                        color = "black"
                        if val.startswith('+') or (not val.startswith('-') and val != "0" and val != "0,00" and not is_cyl):
                            color = "green"
                        elif val.startswith('-') or is_cyl:
                            color = "red"
                        return f"<span style='color:{color};'>{val}</span>"
                    
                    # Display prescription values
                    st.markdown(f"""
                    <div style="font-size: 0.9em;">
                        <strong>Longe</strong>
                        <table style="width:100%; text-align: center;">
                            <thead style="border-bottom: 1px solid #ddd;">
                                <tr><th>Olho</th><th>Esférico</th><th>Cilíndrico</th><th>Eixo</th><th>DNP</th><th>Altura</th></tr>
                            </thead>
                            <tbody>
                                <tr><td><b>OD</b></td><td>{fmt_val(row['od_sph'])}</td><td>{fmt_val(row['od_cyl'], True)}</td><td>{row['od_axis']}</td><td>{row['od_dnp']}</td><td>{row['od_height']}</td></tr>
                                <tr><td><b>OE</b></td><td>{fmt_val(row['oe_sph'])}</td><td>{fmt_val(row['oe_cyl'], True)}</td><td>{row['oe_axis']}</td><td>{row['oe_dnp']}</td><td>{row['oe_height']}</td></tr>
                            </tbody>
                        </table>
                        <div style="margin: 10px 0; text-align: center;">
                            <b>Adição:</b> {fmt_val(row['addition'])}
                        </div>
                        <strong>Perto</strong>
                        <table style="width:100%; text-align: center;">
                            <thead style="border-bottom: 1px solid #ddd;">
                                <tr><th>Olho</th><th>Esférico</th><th>Cilíndrico</th><th>Eixo</th><th>DNP</th><th>-</th></tr>
                            </thead>
                            <tbody>
                                <tr><td><b>OD</b></td><td>{fmt_val(row['od_perto_sph'])}</td><td>{fmt_val(row['od_perto_cyl'], True)}</td><td>{row['od_perto_axis']}</td><td>{row['od_perto_dnp']}</td><td>-</td></tr>
                                <tr><td><b>OE</b></td><td>{fmt_val(row['oe_perto_sph'])}</td><td>{fmt_val(row['oe_perto_cyl'], True)}</td><td>{row['oe_perto_axis']}</td><td>{row['oe_perto_dnp']}</td><td>-</td></tr>
                            </tbody>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if row['notes']:
                        st.caption(f"📝 {row['notes']}")
    else:
        st.warning("Nenhuma receita encontrada com os critérios de busca.")

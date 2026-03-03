import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase() -> Client:
    """Returns a cached Supabase client using credentials from Streamlit secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

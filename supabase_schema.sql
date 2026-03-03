-- ============================================================
-- Schema SQL - Ótica Shirlene
-- Execute isso no Supabase SQL Editor (supabase.com → SQL Editor)
-- ============================================================

-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clients (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    cpf TEXT,
    rg TEXT,
    birth_date TEXT,
    sex TEXT,
    address TEXT,
    address_number TEXT,
    neighborhood TEXT,
    credit_balance REAL DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de telefones dos clientes
CREATE TABLE IF NOT EXISTS client_phones (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT REFERENCES clients(id) ON DELETE CASCADE,
    number TEXT,
    complement TEXT
);

-- Tabela de profissionais
CREATE TABLE IF NOT EXISTS professionals (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de receitas
CREATE TABLE IF NOT EXISTS prescriptions (
    id BIGSERIAL PRIMARY KEY,
    client_id BIGINT REFERENCES clients(id) ON DELETE CASCADE,
    exam_date TEXT,
    expiration_date TEXT,
    professional TEXT,

    -- Longe
    od_sph TEXT, od_cyl TEXT, od_axis TEXT, od_dnp TEXT, od_height TEXT,
    oe_sph TEXT, oe_cyl TEXT, oe_axis TEXT, oe_dnp TEXT, oe_height TEXT,

    -- Adição
    addition TEXT,

    -- Perto
    od_perto_sph TEXT, od_perto_cyl TEXT, od_perto_axis TEXT, od_perto_dnp TEXT,
    oe_perto_sph TEXT, oe_perto_cyl TEXT, oe_perto_axis TEXT, oe_perto_dnp TEXT,

    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Permitir acesso público (necessário para o Streamlit funcionar com anon key)
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_phones ENABLE ROW LEVEL SECURITY;
ALTER TABLE professionals ENABLE ROW LEVEL SECURITY;
ALTER TABLE prescriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all_clients" ON clients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_phones" ON client_phones FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_professionals" ON professionals FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_prescriptions" ON prescriptions FOR ALL USING (true) WITH CHECK (true);

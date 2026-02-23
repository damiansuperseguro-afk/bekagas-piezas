import streamlit as st
import pandas as pd
import psycopg2
import os

st.set_page_config(layout="wide")

# -------- CONEXIÓN A BASE DE DATOS --------
def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ["DB_PORT"]
    )

# -------- LOGIN SIMPLE --------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("Bekagas Instalaciones - Piezas")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        if user == "bekagas" and password == "piezas2026":
            st.session_state.login = True
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# -------- APP PRINCIPAL --------
st.image("logo.png", use_column_width=True)
st.title("Gestión de Piezas")

conn = get_connection()

buscar = st.text_input("🔎 Buscar modelo, código o pieza")

query = """
SELECT * FROM piezas
WHERE modelo ILIKE %s
OR nombre_pieza ILIKE %s
OR codigo ILIKE %s
"""

df = pd.read_sql(
    query,
    conn,
    params=(f"%{buscar}%", f"%{buscar}%", f"%{buscar}%")
)

for index, row in df.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([3,1])

    col1.write(f"**Modelo:** {row['modelo']}")
    col1.write(f"**Pieza:** {row['nombre_pieza']}")
    col1.write(f"**Código:** {row['codigo']}")
    col1.write(f"**Precio:** {row['precio']} €")

    stock_color = "red" if row["stock"] <= row["stock_minimo"] else "green"
    col1.markdown(
        f"**Stock:** <span style='color:{stock_color}'>{row['stock']}</span>",
        unsafe_allow_html=True
    )

    if col2.button("➕", key=f"add{row['id']}"):
        cursor = conn.cursor()
        cursor.execute("UPDATE piezas SET stock = stock + 1 WHERE id = %s", (row["id"],))
        conn.commit()
        st.rerun()

    if col2.button("➖", key=f"sub{row['id']}"):
        cursor = conn.cursor()
        cursor.execute("UPDATE piezas SET stock = stock - 1 WHERE id = %s", (row["id"],))
        conn.commit()
        st.rerun()

st.subheader("🚨 Piezas con poco stock")
alertas = pd.read_sql(
    "SELECT * FROM piezas WHERE stock <= stock_minimo",
    conn
)
st.dataframe(alertas)

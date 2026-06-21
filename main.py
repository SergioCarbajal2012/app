import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

if not firebase_admin._apps:
    # Si estamos en Streamlit Cloud, usamos los Secretos del sistema
    if "firebase" in st.secrets:
        firebase_details = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_details)
    # Si estamos en local, usamos el archivo JSON
    else:
        cred = credentials.Certificate('firebase_key.json')
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
coleccion_alertas = db.collection('alertas_elt')

st.title("📱 ELT Monitor App - Gestión de Alertas")

# READ: Mostrar Alertas Actuales
st.header("Historial de Alertas de Linaje")
alertas_ref = coleccion_alertas.stream()
for alerta in alertas_ref:
    data = alerta.to_dict()
    st.write(f"**ID:** {alerta.id} | **Capa:** {data['capa']} | **Estado:** {data['estado']} | **Mensaje:** {data['mensaje']}")

st.divider()

# CREATE: Registrar nueva alerta
st.header("Crear Nueva Alerta")
with st.form("form_crear"):
    capa_input = st.selectbox("Capa afectada", ["STG", "PSA", "DWH", "BWH", "DMT"])
    mensaje_input = st.text_input("Descripción del error")
    if st.form_submit_button("Registrar Alerta"):
        coleccion_alertas.add({"capa": capa_input, "mensaje": mensaje_input, "estado": "Pendiente"})
        st.success("¡Alerta registrada en Firebase!")
        st.rerun()

st.divider()

# UPDATE & DELETE: Gestionar alertas existentes
st.header("Gestión de Tickets")
id_modificar = st.text_input("ID del Ticket a gestionar")
col1, col2 = st.columns(2)

with col1:
    nuevo_estado = st.selectbox("Nuevo Estatus", ["En revisión", "Resuelto"])
    if st.button("Actualizar Estatus"):
        if id_modificar:
            coleccion_alertas.document(id_modificar).update({"estado": nuevo_estado})
            st.success("Ticket actualizado.")
            st.rerun()

with col2:
    if st.button("Eliminar Registro (Falso Positivo)"):
        if id_modificar:
            coleccion_alertas.document(id_modificar).delete()
            st.warning("Ticket eliminado de la base de datos.")
            st.rerun()

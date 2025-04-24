import streamlit as st
import pandas as pd
import datetime
import os

# Archivos de datos
archivo_csv = "registro_pagos.csv"
archivo_proveedores = "/mnt/data/Listado de Proveedores.xlsx"
archivo_tipos_pago = "tipos_pago.csv"
carpeta_respaldo = "respaldos_pagos"

# Crear carpeta de respaldos si no existe
if not os.path.exists(carpeta_respaldo):
    os.makedirs(carpeta_respaldo)

# Cargar datos de pagos existentes o crear archivo nuevo
columnas_base = [
    "Fecha", "Proveedor", "Monto", "Medio de Pago",
    "Tipo de Pago", "Factura Asociada", "Concepto",
    "Archivo Respaldo", "Marcado por Responsable", "Marcado por Colaboradora"
]
if os.path.exists(archivo_csv):
    df = pd.read_csv(archivo_csv)
    for col in columnas_base:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=columnas_base)
    df.to_csv(archivo_csv, index=False)

# Cargar listado de proveedores
try:
    df_proveedores = pd.read_excel(archivo_proveedores, skiprows=1)
    lista_proveedores = df_proveedores["Unnamed: 2"].dropna().unique().tolist()
except Exception as e:
    df_proveedores = pd.DataFrame(columns=["Código", "Código Real", "Nombre", "Estado", "Saldo"])
    lista_proveedores = []

# Cargar tipos de pago existentes o crear archivo nuevo
if os.path.exists(archivo_tipos_pago):
    tipos_pago_df = pd.read_csv(archivo_tipos_pago)
    lista_tipos_pago = tipos_pago_df["Tipo"].dropna().unique().tolist()
else:
    lista_tipos_pago = [
        "Factura", "Anticipo", "Compra menor", "Rendición", "Traspaso entre cuentas", "Préstamo recibido", "Otro"
    ]
    tipos_pago_df = pd.DataFrame({"Tipo": lista_tipos_pago})
    tipos_pago_df.to_csv(archivo_tipos_pago, index=False)

st.title("📒 Registro de Pagos - CFC")

# --- Formulario de ingreso ---
with st.form("registro_form"):
    st.subheader("Registrar nuevo pago")
    fecha = st.date_input("Fecha del pago", value=datetime.date.today())
    proveedor = st.text_input("Proveedor", placeholder="Escriba o seleccione un proveedor")
    proveedor_sugerido = st.selectbox("Buscar proveedor en listado", [""] + lista_proveedores)
    if proveedor_sugerido:
        proveedor = proveedor_sugerido

    monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%0.0f")
    medio_pago = st.selectbox("Medio de pago", [
        "Caja chica", "Banco Chile", "Banco Bci", "Banco Scotia",
        "Tarjeta Crédito Chile", "Tarjeta Crédito Bci", "Tarjeta Crédito Scotia"
    ])
    tipo_pago = st.text_input("Tipo de pago", placeholder="Escriba o seleccione un tipo de pago")
    tipo_pago_sugerido = st.selectbox("Buscar tipo de pago en listado", [""] + lista_tipos_pago)
    if tipo_pago_sugerido:
        tipo_pago = tipo_pago_sugerido

    factura = st.text_input("Factura asociada (opcional)")
    concepto = st.text_area("Concepto u observación")
    archivo_respaldo = st.file_uploader("Subir respaldo del pago (PDF, imagen, etc.)", type=["pdf", "jpg", "jpeg", "png"])
    marcado_responsable = st.checkbox("✅ Ya fue ingresado por mí en la ERP")
    marcado_colaboradora = st.checkbox("✅ Confirmado por colaboradora en ERP")

    enviar = st.form_submit_button("Guardar pago")

    if enviar:
        archivo_guardado = ""
        if archivo_respaldo:
            nombre_archivo = f"{fecha}_{proveedor}_{archivo_respaldo.name}"
            ruta_archivo = os.path.join(carpeta_respaldo, nombre_archivo)
            with open(ruta_archivo, "wb") as f:
                f.write(archivo_respaldo.getbuffer())
            archivo_guardado = ruta_archivo

        nuevo = pd.DataFrame.from_dict([{
            "Fecha": fecha,
            "Proveedor": proveedor,
            "Monto": monto,
            "Medio de Pago": medio_pago,
            "Tipo de Pago": tipo_pago,
            "Factura Asociada": factura,
            "Concepto": concepto,
            "Archivo Respaldo": archivo_guardado,
            "Marcado por Responsable": "Sí" if marcado_responsable else "",
            "Marcado por Colaboradora": "Sí" if marcado_colaboradora else ""
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(archivo_csv, index=False)
        st.success("✅ Pago registrado correctamente")

        if proveedor not in lista_proveedores:
            nuevo_proveedor = pd.DataFrame.from_dict([{
                "Código": "",
                "Código Real": "",
                "Nombre": proveedor,
                "Estado": "Activo",
                "Saldo": 0
            }])
            df_proveedores = pd.concat([df_proveedores, nuevo_proveedor], ignore_index=True)
            df_proveedores.to_excel(archivo_proveedores, index=False)
            st.info(f"📝 Proveedor '{proveedor}' agregado al listado.")

        if tipo_pago not in lista_tipos_pago:
            nuevo_tipo = pd.DataFrame.from_dict([{ "Tipo": tipo_pago }])
            tipos_pago_df = pd.concat([tipos_pago_df, nuevo_tipo], ignore_index=True)
            tipos_pago_df.to_csv(archivo_tipos_pago, index=False)
            st.info(f"📝 Tipo de pago '{tipo_pago}' agregado al listado.")

# --- Filtros ---
st.subheader("📋 Pagos registrados")
filtro_colab = st.checkbox("👀 Mostrar solo pagos pendientes para colaboradora")
fecha_inicio = st.date_input("Desde", value=pd.to_datetime(df["Fecha"]).min() if not df.empty else datetime.date.today())
fecha_fin = st.date_input("Hasta", value=pd.to_datetime(df["Fecha"]).max() if not df.empty else datetime.date.today())
filtro_proveedor = st.selectbox("Filtrar por proveedor", ["Todos"] + sorted(set(df["Proveedor"])))
filtro_tipo_pago = st.selectbox("Filtrar por tipo de pago", ["Todos"] + sorted(set(df["Tipo de Pago"])))

# --- Visualización de registros ---
with st.expander("Ver listado de pagos"):
    if not df.empty:
        df_vista = df.copy()
        df_vista["Fecha"] = pd.to_datetime(df_vista["Fecha"])
        df_vista = df_vista[(df_vista["Fecha"] >= pd.to_datetime(fecha_inicio)) & (df_vista["Fecha"] <= pd.to_datetime(fecha_fin))]
        if filtro_colab:
            df_vista = df_vista[df_vista["Marcado por Colaboradora"] != "Sí"]
        if filtro_proveedor != "Todos":
            df_vista = df_vista[df_vista["Proveedor"] == filtro_proveedor]
        if filtro_tipo_pago != "Todos":
            df_vista = df_vista[df_vista["Tipo de Pago"] == filtro_tipo_pago]
        df_vista["Archivo Respaldo"] = df_vista["Archivo Respaldo"].apply(
            lambda x: f"[Abrir]({x})" if pd.notna(x) and x != "" else ""
        )
        st.markdown(df_vista.to_markdown(index=False), unsafe_allow_html=True)
    else:
        st.info("No hay pagos registrados aún.")

# --- Exportar ---
st.download_button(
    label="📥 Descargar Excel con registros",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='registro_pagos.csv',
    mime='text/csv'
)  

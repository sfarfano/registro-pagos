import streamlit as st
import pandas as pd
import datetime
import os

# Archivos de datos
archivo_csv = "registro_pagos.csv"
archivo_personal = "gastos_personales.csv"
archivo_proveedores = "Listado de Proveedores.xlsx"
archivo_tipos_pago = "tipos_pago.csv"
carpeta_respaldo = "respaldos_pagos"
usuarios_autorizados = ["soledad", "admin"]

# Crear carpeta de respaldos si no existe
if not os.path.exists(carpeta_respaldo):
    os.makedirs(carpeta_respaldo)

# Inicio de sesión básico
st.sidebar.title("🔐 Ingreso de usuario")
usuario = st.sidebar.text_input("Nombre de usuario")
es_admin = usuario.strip().lower() in usuarios_autorizados

if not usuario:
    st.warning("Por favor, escribe tu nombre de usuario para comenzar.")
    st.stop()

# --- Sección exclusiva para gastos personales ---
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Volver a panel principal"):
    st.session_state.seccion = ""

if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

if usuario.strip().lower() == "soledad":
    st.sidebar.markdown("---")
    if st.sidebar.button("🧾 Registrar gastos personales"):
        st.session_state.seccion = "gastos_personales"

if st.session_state.get("seccion") == "gastos_personales":
    st.title("🧾 Gastos Personales - Rendición Global")
    if os.path.exists(archivo_personal):
        df_personal = pd.read_csv(archivo_personal, dtype=str)
        df_personal["Fecha"] = pd.to_datetime(df_personal["Fecha"], errors="coerce", format="%Y-%m-%d")
    else:
        df_personal = pd.DataFrame(columns=["Fecha", "Categoría", "Detalle", "Monto"])

    with st.form("form_gasto_perso"):
        fecha_p = st.date_input("Fecha del gasto", value=datetime.date.today())
        categoria = st.selectbox("Categoría", ["Estacionamiento", "Colación", "Uber", "Pasajes", "Otro"])
        detalle = st.text_input("Detalle o comentario")
        monto = st.number_input("Monto ($)", min_value=0.0, step=100.0, format="%0.0f")
        guardar_p = st.form_submit_button("Guardar gasto")

        if guardar_p:
            nuevo = pd.DataFrame.from_dict([{
                "Fecha": fecha_p,
                "Categoría": categoria,
                "Detalle": detalle,
                "Monto": monto
            }])
            df_personal = pd.concat([df_personal, nuevo], ignore_index=True)
            df_personal["Fecha"] = pd.to_datetime(df_personal["Fecha"]).dt.strftime("%Y-%m-%d")
            df_personal.to_csv(archivo_personal, index=False)
            st.success("✅ Gasto registrado")

    st.subheader("📋 Listado de gastos personales")
    st.dataframe(df_personal)
    st.download_button(
        label="📥 Descargar Excel de gastos personales",
        data=df_personal.to_csv(index=False).encode('utf-8'),
        file_name='gastos_personales.csv',
        mime='text/csv'
    )
    st.stop()

# --- Registro de pagos ---

# Cargar datos de pagos existentes o crear archivo nuevo
fecha_formato = "%Y-%m-%d"
columnas_base = [
    "Fecha", "Proveedor", "Monto", "Medio de Pago",
    "Tipo de Pago", "Factura Asociada", "Concepto",
    "Archivo Respaldo", "Marcado por Responsable", "Marcado por Colaboradora", "Registrado por"
]
if os.path.exists(archivo_csv):
    df = pd.read_csv(archivo_csv, dtype=str)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", format=fecha_formato)
    for col in columnas_base:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=columnas_base)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", format=fecha_formato)
    df = pd.DataFrame(columns=columnas_base)
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce", format=fecha_formato)
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime(fecha_formato)
df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime(fecha_formato)
df.to_csv(archivo_csv, index=False)

# Cargar listado de proveedores correctamente
try:
    df_proveedores = pd.read_excel(archivo_proveedores)
    lista_proveedores = df_proveedores["Nombre"].dropna().unique().tolist() if "Nombre" in df_proveedores.columns else []
except:
    lista_proveedores = []

# Cargar tipos de pago existentes o crear archivo nuevo
if os.path.exists(archivo_tipos_pago):
    tipos_pago_df = pd.read_csv(archivo_tipos_pago)
    lista_tipos_pago = tipos_pago_df["Tipo"].dropna().unique().tolist()
else:
    lista_tipos_pago = [
        "Ajuste contable",
        "Factura", "Anticipo", "Compra menor", "Rendición", "Traspaso entre cuentas", "Préstamo recibido", "Otro"
    ]
    tipos_pago_df = pd.DataFrame({"Tipo": lista_tipos_pago})
    tipos_pago_df.to_csv(archivo_tipos_pago, index=False)

st.title("📒 Registro de Pagos - CFC")

# --- Formulario de ingreso ---
with st.form("registro_form"):
    mostrar_proveedor = True
    st.subheader("Registrar nuevo pago")
    fecha = st.date_input("Fecha del pago", value=datetime.date.today())
    if mostrar_proveedor:
        proveedor = st.text_input("Proveedor", placeholder="Escriba o seleccione un proveedor")
        proveedor_sugerido = st.selectbox("Buscar proveedor en listado", [""] + lista_proveedores)
        if proveedor_sugerido:
            proveedor = proveedor_sugerido
    else:
        proveedor = tipo_pago_sugerido

    monto = st.number_input("Monto", min_value=0.0, step=100.0, format="%0.0f")
    medio_pago = st.selectbox("Medio de pago", [
        "Caja chica", "Banco Chile", "Banco Bci", "Banco Scotia",
        "Tarjeta Crédito Chile", "Tarjeta Crédito Bci", "Tarjeta Crédito Scotia"
    ])
    tipo_pago = st.text_input("Tipo de pago", placeholder="Escriba o seleccione un tipo de pago")
    tipo_pago_sugerido = st.selectbox("Buscar tipo de pago en listado", [""] + lista_tipos_pago)
    if tipo_pago_sugerido in ["Ajuste contable", "Traspaso entre cuentas", "Préstamo recibido"]:
        mostrar_proveedor = False
    if tipo_pago_sugerido:
        tipo_pago = tipo_pago_sugerido

    factura = st.text_input("Factura asociada (opcional)")
    concepto = st.text_area("Concepto u observación")
    archivo_respaldo = st.file_uploader("Subir respaldo del pago (PDF, imagen, etc.)", type=["pdf", "jpg", "jpeg", "png"])
    marcado_responsable = st.checkbox("✅ Ya fue ingresado por mí en la ERP")
    marcado_colaboradora = st.checkbox("✅ Confirmado por colaboradora en ERP")

    enviar = st.form_submit_button("Guardar pago")

    if enviar:
        if monto == 0:
            st.warning("⚠️ El monto no puede ser cero. Por favor, ingresa un valor válido.")
            st.stop()
        if mostrar_proveedor and not proveedor.strip():
            st.warning("⚠️ Debes ingresar o seleccionar un proveedor.")
            st.stop()
        if not tipo_pago.strip():
            st.warning("⚠️ Debes ingresar o seleccionar un tipo de pago.")
            st.stop()

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
            "Marcado por Colaboradora": "Sí" if marcado_colaboradora else "",
            "Registrado por": usuario
        }])
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(archivo_csv, index=False)
        st.success("✅ Pago registrado correctamente")
# ... se conserva igual del archivo original anterior que ya habías cargado

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

st.subheader("📊 Resumen de movimientos externos")
if not df_externos.empty:
    df_externos["Archivo Respaldo"] = df_externos["Archivo Respaldo"].apply(
        lambda x: f"[Abrir]({x})" if pd.notna(x) and x != "" else ""
    )
    st.dataframe(
        df_externos.style.applymap(lambda val: "background-color: #e8f5e9;", subset=["Tipo de Pago"])
    )
    st.download_button(
        label="⬇️ Descargar movimientos externos",
        data=df_externos.to_csv(index=False).encode('utf-8'),
        file_name='movimientos_externos.csv',
        mime='text/csv'
    )
else:
    st.info("No hay movimientos externos registrados.")

# Sección adicional para separar internos
df_internos = df[df["Tipo de Pago"].isin(["Ajuste contable", "Traspaso entre cuentas", "Préstamo recibido"])]
df_externos = df[~df["Tipo de Pago"].isin(["Ajuste contable", "Traspaso entre cuentas", "Préstamo recibido"])]

st.subheader("📊 Resumen de movimientos internos")
if not df_internos.empty:
    df_internos["Archivo Respaldo"] = df_internos["Archivo Respaldo"].apply(
        lambda x: f"[Abrir]({x})" if pd.notna(x) and x != "" else ""
    )
    st.dataframe(
        df_internos.style.applymap(lambda val: "background-color: #fce4ec;", subset=["Tipo de Pago"])
    )
    st.download_button(
        label="⬇️ Descargar movimientos internos",
        data=df_internos.to_csv(index=False).encode('utf-8'),
        file_name='movimientos_internos.csv',
        mime='text/csv'
    )
else:
    st.info("No hay movimientos internos registrados.")
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

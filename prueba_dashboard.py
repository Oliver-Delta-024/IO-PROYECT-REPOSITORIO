import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Optimización Textil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏭 Dashboard de Optimización Textil - ICATEX")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    # Leer todas las hojas del Excel
    file_path = "ICATEX_Datos_Completos_20Productos.xlsx"
    
    data = {}
    sheets = [
        'PRODUCTOS', 'INSUMOS', 'PROCESOS', 'CONSUMO_INSUMOS', 'TIEMPO_PROCESOS',
        'DEMANDA_2021', 'DEMANDA_2022', 'DEMANDA_2023', 'DEMANDA_2024',
        'CAPACIDAD_2021', 'CAPACIDAD_2022', 'CAPACIDAD_2023', 'CAPACIDAD_2024',
        'COSTOS_2021', 'COSTOS_2022', 'COSTOS_2023', 'COSTOS_2024'
    ]
    
    for sheet in sheets:
        data[sheet] = pd.read_excel(file_path, sheet_name=sheet)
    
    return data

# Cargar los datos
data = load_data()

# Sidebar para navegación
st.sidebar.title("📊 Navegación")
section = st.sidebar.radio(
    "Selecciona una sección:",
    ["📈 Resumen General", "👕 Análisis de Productos", "💰 Análisis de Costos", 
     "📊 Análisis de Demanda", "⚙️ Análisis de Procesos", "🔍 Escenarios y Simulaciones"]
)

# Función para formatear números
def format_currency(value):
    return f"S/ {value:.2f}"

# ===== SECCIÓN 1: RESUMEN GENERAL =====
if section == "📈 Resumen General":
    st.header("📈 Resumen General del Negocio")
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_productos = len(data['PRODUCTOS'])
        st.metric("Total de Productos", total_productos)
    
    with col2:
        total_insumos = len(data['INSUMOS'])
        st.metric("Total de Insumos", total_insumos)
    
    with col3:
        total_procesos = len(data['PROCESOS'])
        st.metric("Procesos Productivos", total_procesos)
    
    with col4:
        años_cobertura = "2021-2024"
        st.metric("Período Analizado", años_cobertura)
    
    # Gráfico de productos por categoría
    st.subheader("📦 Distribución de Productos")
    col1, col2 = st.columns(2)
    
    with col1:
        cat_dist = data['PRODUCTOS']['Categoria'].value_counts()
        fig_cat = px.pie(values=cat_dist.values, names=cat_dist.index, 
                        title="Productos por Categoría")
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        linea_dist = data['PRODUCTOS']['Linea'].value_counts()
        fig_linea = px.bar(x=linea_dist.index, y=linea_dist.values,
                          title="Productos por Línea")
        st.plotly_chart(fig_linea, use_container_width=True)
    
    # Tiempos de producción
    st.subheader("⏱️ Análisis de Tiempos de Producción")
    fig_tiempos = px.box(data['PRODUCTOS'], y='TiempoProd_Total(min)', 
                        title="Distribución de Tiempos de Producción")
    st.plotly_chart(fig_tiempos, use_container_width=True)

# ===== SECCIÓN 2: ANÁLISIS DE PRODUCTOS =====
elif section == "👕 Análisis de Productos":
    st.header("👕 Análisis Detallado de Productos")
    
    # Selector de producto
    productos = data['PRODUCTOS']['Nombre_Producto'].tolist()
    producto_seleccionado = st.selectbox("Selecciona un producto:", productos)
    
    if producto_seleccionado:
        producto_info = data['PRODUCTOS'][data['PRODUCTOS']['Nombre_Producto'] == producto_seleccionado].iloc[0]
        producto_id = producto_info['ID_Producto']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Categoría", producto_info['Categoria'])
        with col2:
            st.metric("Línea", producto_info['Linea'])
        with col3:
            st.metric("Tiempo Producción", f"{producto_info['TiempoProd_Total(min)']} min")
        with col4:
            st.metric("ID Producto", producto_id)
        
        # Información de insumos
        st.subheader("📦 Insumos Requeridos")
        insumos_producto = data['CONSUMO_INSUMOS'][data['CONSUMO_INSUMOS']['ID_Producto'] == producto_id]
        insumos_detalle = insumos_producto.merge(data['INSUMOS'], on='ID_Insumo')
        
        if not insumos_detalle.empty:
            fig_insumos = px.bar(insumos_detalle, x='Nombre_Insumo', y='Cantidad_Requerida',
                                title=f"Insumos para {producto_seleccionado}")
            st.plotly_chart(fig_insumos, use_container_width=True)
            
            # Mostrar tabla de insumos
            st.dataframe(insumos_detalle[['Nombre_Insumo', 'Unidad_Medida', 'Cantidad_Requerida', 'Costo_Unitario(S/)']])
        
        # Tiempos por proceso
        st.subheader("⚙️ Tiempos por Proceso")
        tiempos_proceso = data['TIEMPO_PROCESOS'][data['TIEMPO_PROCESOS']['ID_Producto'] == producto_id]
        tiempos_detalle = tiempos_proceso.merge(data['PROCESOS'], on='ID_Proceso')
        
        if not tiempos_detalle.empty:
            fig_procesos = px.bar(tiempos_detalle, x='Nombre_Proceso', y='Tiempo_Minutos',
                                 title=f"Tiempos de Proceso para {producto_seleccionado}")
            st.plotly_chart(fig_procesos, use_container_width=True)

# ===== SECCIÓN 3: ANÁLISIS DE COSTOS =====
elif section == "💰 Análisis de Costos":
    st.header("💰 Análisis de Costos y Rentabilidad")
    
    # Selector de año
    año = st.selectbox("Selecciona el año:", [2021, 2022, 2023, 2024])
    
    # Obtener datos de costos del año seleccionado
    costos_año = data[f'COSTOS_{año}']
    demanda_año = data[f'DEMANDA_{año}']
    
    # Merge para obtener información completa
    costos_completos = costos_año.merge(demanda_año, on=['ID_Producto', 'Mes'])
    costos_completos = costos_completos.merge(data['PRODUCTOS'][['ID_Producto', 'Nombre_Producto', 'Categoria']], on='ID_Producto')
    
    # Calcular margen
    costos_completos['Margen(S/)'] = costos_completos['Precio_Venta(S/)'] - costos_completos['Costo_Total(S/)']
    costos_completos['Margen_Porcentaje'] = (costos_completos['Margen(S/)'] / costos_completos['Precio_Venta(S/)']) * 100
    
    # Métricas de costos
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        costo_promedio = costos_completos['Costo_Total(S/)'].mean()
        st.metric("Costo Promedio", format_currency(costo_promedio))
    with col2:
        precio_promedio = costos_completos['Precio_Venta(S/)'].mean()
        st.metric("Precio Venta Promedio", format_currency(precio_promedio))
    with col3:
        margen_promedio = costos_completos['Margen(S/)'].mean()
        st.metric("Margen Promedio", format_currency(margen_promedio))
    with col4:
        margen_porc_promedio = costos_completos['Margen_Porcentaje'].mean()
        st.metric("Margen % Promedio", f"{margen_porc_promedio:.1f}%")
    
    # Gráficos de costos
    st.subheader("📊 Evolución de Costos y Margenes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Costos promedio por mes
        costos_mensuales = costos_completos.groupby('Mes').agg({
            'Costo_Total(S/)': 'mean',
            'Precio_Venta(S/)': 'mean',
            'Margen(S/)': 'mean'
        }).reset_index()
        
        fig_costos = go.Figure()
        fig_costos.add_trace(go.Scatter(x=costos_mensuales['Mes'], y=costos_mensuales['Costo_Total(S/)'], 
                                       name='Costo Total', line=dict(color='red')))
        fig_costos.add_trace(go.Scatter(x=costos_mensuales['Mes'], y=costos_mensuales['Precio_Venta(S/)'], 
                                       name='Precio Venta', line=dict(color='green')))
        fig_costos.add_trace(go.Scatter(x=costos_mensuales['Mes'], y=costos_mensuales['Margen(S/)'], 
                                       name='Margen', line=dict(color='blue')))
        fig_costos.update_layout(title=f"Evolución de Costos y Precios - {año}")
        st.plotly_chart(fig_costos, use_container_width=True)
    
    with col2:
        # Margen por categoría
        margen_categoria = costos_completos.groupby('Categoria')['Margen_Porcentaje'].mean().reset_index()
        fig_margen_cat = px.bar(margen_categoria, x='Categoria', y='Margen_Porcentaje',
                               title=f"Margen Promedio por Categoría - {año}")
        st.plotly_chart(fig_margen_cat, use_container_width=True)
    
    # Top productos más rentables
    st.subheader("🏆 Productos Más Rentables")
    rentabilidad_productos = costos_completos.groupby(['ID_Producto', 'Nombre_Producto']).agg({
        'Margen_Porcentaje': 'mean',
        'Margen(S/)': 'mean',
        'Costo_Total(S/)': 'mean'
    }).reset_index().sort_values('Margen_Porcentaje', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Top 10 Productos por Margen %")
        top_10_margen = rentabilidad_productos.head(10)
        fig_top_margen = px.bar(top_10_margen, x='Nombre_Producto', y='Margen_Porcentaje',
                               title="Top 10 Productos por Margen %")
        st.plotly_chart(fig_top_margen, use_container_width=True)
    
    with col2:
        st.write("Top 10 Productos por Margen Absoluto")
        top_10_absoluto = rentabilidad_productos.nlargest(10, 'Margen(S/)')
        fig_top_absoluto = px.bar(top_10_absoluto, x='Nombre_Producto', y='Margen(S/)',
                                 title="Top 10 Productos por Margen Absoluto")
        st.plotly_chart(fig_top_absoluto, use_container_width=True)

# ===== SECCIÓN 4: ANÁLISIS DE DEMANDA =====
elif section == "📊 Análisis de Demanda":
    st.header("📊 Análisis de Demanda")
    
    # Selector de producto para análisis de demanda
    producto_demanda = st.selectbox("Selecciona producto para análisis:", 
                                   data['PRODUCTOS']['Nombre_Producto'].tolist())
    
    if producto_demanda:
        producto_id = data['PRODUCTOS'][data['PRODUCTOS']['Nombre_Producto'] == producto_demanda].iloc[0]['ID_Producto']
        
        # Combinar datos de demanda de todos los años
        demanda_total = pd.concat([
            data['DEMANDA_2021'],
            data['DEMANDA_2022'],
            data['DEMANDA_2023'],
            data['DEMANDA_2024']
        ])
        
        # Filtrar por producto seleccionado
        demanda_producto = demanda_total[demanda_total['ID_Producto'] == producto_id].copy()
        
        # Ordenar por año y mes
        meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        demanda_producto['Mes'] = pd.Categorical(demanda_producto['Mes'], categories=meses_orden, ordered=True)
        
        # Crear año para el gráfico
        años = [2021] * 12 + [2022] * 12 + [2023] * 12 + [2024] * 12
        demanda_producto = demanda_producto.sort_values('Mes')
        demanda_producto['Año'] = años
        
        st.subheader(f"📈 Evolución de la Demanda - {producto_demanda}")
        
        fig_demanda = go.Figure()
        fig_demanda.add_trace(go.Scatter(x=demanda_producto['Mes'], y=demanda_producto['Demanda_Minima'], 
                                        name='Demanda Mínima', line=dict(color='orange')))
        fig_demanda.add_trace(go.Scatter(x=demanda_producto['Mes'], y=demanda_producto['Demanda_Maxima'], 
                                        name='Demanda Máxima', line=dict(color='red')))
        fig_demanda.update_layout(title=f"Demanda Mínima y Máxima por Mes - {producto_demanda}",
                                 xaxis_title="Mes", yaxis_title="Demanda")
        st.plotly_chart(fig_demanda, use_container_width=True)
        
        # Análisis estacionalidad
        st.subheader("🔄 Análisis de Estacionalidad")
        
        demanda_promedio = demanda_producto.groupby('Mes').agg({
            'Demanda_Minima': 'mean',
            'Demanda_Maxima': 'mean'
        }).reset_index()
        
        fig_estacionalidad = go.Figure()
        fig_estacionalidad.add_trace(go.Scatter(x=demanda_promedio['Mes'], y=demanda_promedio['Demanda_Minima'], 
                                              name='Demanda Mínima Promedio', line=dict(color='lightblue')))
        fig_estacionalidad.add_trace(go.Scatter(x=demanda_promedio['Mes'], y=demanda_promedio['Demanda_Maxima'], 
                                              name='Demanda Máxima Promedio', line=dict(color='darkblue')))
        fig_estacionalidad.update_layout(title="Patrón de Estacionalidad Promedio (2021-2024)")
        st.plotly_chart(fig_estacionalidad, use_container_width=True)

# ===== SECCIÓN 5: ANÁLISIS DE PROCESOS =====
elif section == "⚙️ Análisis de Procesos":
    st.header("⚙️ Análisis de Procesos Productivos")
    
    # Selector de año para capacidad
    año_capacidad = st.selectbox("Selecciona año para análisis de capacidad:", [2021, 2022, 2023, 2024])
    
    capacidad_año = data[f'CAPACIDAD_{año_capacidad}']
    
    # Análisis de capacidad
    st.subheader("🏭 Capacidad de Producción por Proceso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Capacidad promedio por proceso
        capacidad_proceso = capacidad_año.groupby('Nombre_Proceso').agg({
            'Minutos_Disponibles': 'mean',
            'Operarios_Disponibles': 'mean'
        }).reset_index()
        
        fig_capacidad = px.bar(capacidad_proceso, x='Nombre_Proceso', y='Minutos_Disponibles',
                              title=f"Capacidad Promedio por Proceso - {año_capacidad}")
        st.plotly_chart(fig_capacidad, use_container_width=True)
    
    with col2:
        # Operarios por proceso
        fig_operarios = px.bar(capacidad_proceso, x='Nombre_Proceso', y='Operarios_Disponibles',
                              title=f"Operarios por Proceso - {año_capacidad}")
        st.plotly_chart(fig_operarios, use_container_width=True)
    
    # Análisis de costos de procesos
    st.subheader("💰 Costos de Procesos")
    
    procesos = data['PROCESOS']
    fig_costos_procesos = px.bar(procesos, x='Nombre_Proceso', y='Costo_Minuto(S/)',
                                title="Costo por Minuto de Cada Proceso")
    st.plotly_chart(fig_costos_procesos, use_container_width=True)
    
    # Tiempos totales por proceso
    st.subheader("⏱️ Tiempos Totales por Proceso")
    
    tiempos_totales = data['TIEMPO_PROCESOS'].groupby('ID_Proceso')['Tiempo_Minutos'].sum().reset_index()
    tiempos_totales = tiempos_totales.merge(data['PROCESOS'], on='ID_Proceso')
    
    fig_tiempos_totales = px.bar(tiempos_totales, x='Nombre_Proceso', y='Tiempo_Minutos',
                                title="Tiempo Total Requerido por Proceso")
    st.plotly_chart(fig_tiempos_totales, use_container_width=True)

# ===== SECCIÓN 6: ESCENARIOS Y SIMULACIONES =====
else:
    st.header("🔍 Simulador de Escenarios")
    
    st.info("""
    **Simulador de Optimización de Producción**
    Ajusta los parámetros para simular diferentes escenarios de producción y su impacto en costos y rentabilidad.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Parámetros de simulación
        st.subheader("⚙️ Parámetros de Simulación")
        
        producto_sim = st.selectbox("Producto a simular:", 
                                   data['PRODUCTOS']['Nombre_Producto'].tolist())
        
        if producto_sim:
            producto_id = data['PRODUCTOS'][data['PRODUCTOS']['Nombre_Producto'] == producto_sim].iloc[0]['ID_Producto']
            producto_info = data['PRODUCTOS'][data['PRODUCTOS']['Nombre_Producto'] == producto_sim].iloc[0]
            
            # Obtener costos actuales
            costo_actual = data['COSTOS_2024'][data['COSTOS_2024']['ID_Producto'] == producto_id]['Costo_Total(S/)'].mean()
            precio_actual = data['DEMANDA_2024'][data['DEMANDA_2024']['ID_Producto'] == producto_id]['Precio_Venta(S/)'].mean()
            
            st.metric("Costo Actual Promedio", format_currency(costo_actual))
            st.metric("Precio Venta Actual", format_currency(precio_actual))
            
            # Sliders para simulación
            reduccion_insumos = st.slider("Reducción en costos de insumos (%):", 0, 30, 0)
            eficiencia_procesos = st.slider("Mejora en eficiencia de procesos (%):", 0, 20, 0)
            aumento_precio = st.slider("Aumento en precio de venta (%):", 0, 25, 0)
            volumen_produccion = st.slider("Volumen de producción (unidades):", 100, 5000, 1000)
    
    with col2:
        st.subheader("📊 Resultados de la Simulación")
        
        if producto_sim:
            # Cálculos de simulación
            nuevo_costo_insumos = costo_actual * 0.6 * (1 - reduccion_insumos/100)  # 60% del costo son insumos
            nuevo_costo_procesos = costo_actual * 0.4 * (1 - eficiencia_procesos/100)  # 40% del costo son procesos
            nuevo_costo_total = nuevo_costo_insumos + nuevo_costo_procesos
            
            nuevo_precio = precio_actual * (1 + aumento_precio/100)
            nuevo_margen = nuevo_precio - nuevo_costo_total
            nuevo_margen_porc = (nuevo_margen / nuevo_precio) * 100
            
            margen_actual = precio_actual - costo_actual
            margen_actual_porc = (margen_actual / precio_actual) * 100
            
            # Mostrar resultados
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.metric("Costo Actual", format_currency(costo_actual))
                st.metric("Costo Simulado", format_currency(nuevo_costo_total), 
                         delta=format_currency(nuevo_costo_total - costo_actual))
                
            with col_res2:
                st.metric("Margen Actual", f"{margen_actual_porc:.1f}%")
                st.metric("Margen Simulado", f"{nuevo_margen_porc:.1f}%", 
                         delta=f"{(nuevo_margen_porc - margen_actual_porc):.1f}%")
            
            # Gráfico comparativo
            fig_comparativo = go.Figure()
            
            fig_comparativo.add_trace(go.Indicator(
                mode = "number+delta",
                value = nuevo_margen_porc,
                number = {'suffix': "%"},
                delta = {'reference': margen_actual_porc, 'relative': False},
                title = {"text": "Margen<br>Simulado vs Actual"},
                domain = {'row': 0, 'column': 0}))
            
            fig_comparativo.add_trace(go.Indicator(
                mode = "number+delta",
                value = nuevo_costo_total,
                number = {'prefix': "S/ "},
                delta = {'reference': costo_actual, 'relative': False},
                title = {"text": "Costo Total<br>Simulado vs Actual"},
                domain = {'row': 0, 'column': 1}))
            
            fig_comparativo.update_layout(
                grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
                template = {'data' : {'indicator': [{
                    'title': {'text': "Margen"},
                    'mode' : "number+delta+gauge",
                    'delta' : {'reference': 90}}]
                                     }})
            
            st.plotly_chart(fig_comparativo, use_container_width=True)
            
            # Impacto financiero total
            utilidad_actual = margen_actual * volumen_produccion
            utilidad_simulada = nuevo_margen * volumen_produccion
            mejora_utilidad = utilidad_simulada - utilidad_actual
            
            st.success(f"**Impacto en Utilidad Total:** {format_currency(mejora_utilidad)}")

# Footer
st.markdown("---")
st.markdown("### 📋 Resumen de Datos Disponibles")
st.write(f"""
- **Productos:** {len(data['PRODUCTOS'])} productos en {data['PRODUCTOS']['Categoria'].nunique()} categorías
- **Insumos:** {len(data['INSUMOS'])} tipos de insumos
- **Procesos:** {len(data['PROCESOS'])} procesos productivos
- **Período:** Datos históricos desde 2021 hasta 2024
- **Cobertura:** Análisis mensual de demanda, costos y capacidad
""")

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.info("""
**📁 Datos Cargados:**
- 20 Productos textiles
- 15 Insumos diferentes  
- 5 Procesos productivos
- 4 años de datos históricos
- Análisis mensual completo
""")


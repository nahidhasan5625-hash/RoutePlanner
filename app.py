import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# Page Configuration
st.set_page_config(
    page_title="Public Transportation Route Planner",
    page_icon="🚌",
    layout="wide"
)

# App Header
st.markdown("## 🚌 Public Transportation Route Planner")
st.markdown("*(Compute shortest paths, suggest optimized routes, and track vehicle positions)*")
st.divider()

# Graph & Data Setup (Dhaka Transit Nodes)
G = nx.Graph()
nodes_coords = {
    'Uttara': (23.8759, 90.3795),
    'Airport': (23.8450, 90.4003),
    'Banani': (23.7937, 90.4066),
    'Farmgate': (23.7570, 90.3900),
    'Shahbagh': (23.7380, 90.3944),
}

G.add_edge('Uttara', 'Airport', weight=3.0, fare=15)
G.add_edge('Airport', 'Banani', weight=5.5, fare=20)
G.add_edge('Banani', 'Farmgate', weight=4.0, fare=20)
G.add_edge('Farmgate', 'Shahbagh', weight=2.5, fare=15)
G.add_edge('Uttara', 'Banani', weight=8.0, fare=30)

# Initialize Session State to hold route data permanently after click
if 'calculated_path' not in st.session_state:
    st.session_state.calculated_path = []
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0
if 'current_metric' not in st.session_state:
    st.session_state.current_metric = 'weight'

# Layout: Side-by-side columns (Control Panel & Live Map)
col1, col2 = st.columns([1, 1.4], gap="medium")

with col1:
    st.markdown("### 🧭 Control Panel")
    service_mode = st.selectbox("Select Service Mode", ["Optimization Service (Smart Routes)", "Live Vehicle Tracking"])
    
    source = st.selectbox("From", list(nodes_coords.keys()))
    target = st.selectbox("To", list(nodes_coords.keys()), index=2)
    
    opt_type = st.radio("Optimize Based On:", ["Minimum Distance (Weight)", "Minimum Cost (Fare)"])
    metric = 'weight' if 'Distance' in opt_type else 'fare'
    
    find_btn = st.button("Suggest Best Route", use_container_width=True, type="primary")
    
    if find_btn:
        if source == target:
            st.warning("Source and destination cannot be the same!")
            st.session_state.calculated_path = []
        else:
            try:
                st.session_state.calculated_path = nx.shortest_path(G, source=source, target=target, weight=metric)
                st.session_state.total_cost = nx.shortest_path_length(G, source=source, target=target, weight=metric)
                st.session_state.current_metric = metric
            except Exception:
                st.session_state.calculated_path = []

    # Display results if path exists in session state
    if st.session_state.calculated_path:
        st.success(f"**Route:** {' ➔ '.join(st.session_state.calculated_path)}")
        unit = "km" if st.session_state.current_metric == 'weight' else "BDT"
        opt_label = "Distance" if st.session_state.current_metric == 'weight' else "Cost"
        st.metric(f"Total {opt_label}", f"{st.session_state.total_cost} {unit}")

with col2:
    st.markdown("### 🗺️ Live Map & Route Direction")
    
    # Initialize Folium Map centered at Dhaka
    m = folium.Map(location=[23.7800, 90.4000], zoom_start=12, tiles="OpenStreetMap")
    
    # Draw Route Line and Markers using session state path
    if st.session_state.calculated_path:
        path_coords = []
        for node in st.session_state.calculated_path:
            coords = nodes_coords[node]
            path_coords.append(coords)
            # Add Blue Markers for path stations
            folium.Marker(
                coords, 
                popup=node, 
                tooltip=node,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
        
        # DRAW GOOGLE MAPS STYLE BRIGHT GREEN POLYLINE DIRECTION
        folium.PolyLine(
            path_coords, 
            color="#28a745",  # Bright Green Color
            weight=7,         # Thick Line
            opacity=0.9       # Visibility
        ).add_to(m)
    else:
        # Default view showing all station markers when no search is triggered
        for node, coords in nodes_coords.items():
            folium.Marker(
                coords, 
                popup=node, 
                tooltip=node,
                icon=folium.Icon(color="gray", icon="info-sign")
            ).add_to(m)
            
    # Render map cleanly inside Streamlit
    st_folium(m, use_container_width=True, height=500)
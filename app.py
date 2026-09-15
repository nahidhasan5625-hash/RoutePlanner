import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# Page Configuration
st.set_page_config(
    page_title="Smart Public Transportation Route Planner",
    page_icon="🚍",
    layout="wide"
)

# Advanced Custom CSS for Modern UI & Premium Card Look
st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f9;
    }
    .metric-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #28a745;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #28a745;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #218838;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# App Header with Markdown Styling
st.markdown("# 🚍 Smart Public Transportation Route Planner")
st.markdown("##### *Advanced Graph-Based Transit Network Optimization & Live Mapping System*")
st.markdown("---")

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

# Initialize Session State
if 'calculated_path' not in st.session_state:
    st.session_state.calculated_path = []
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0
if 'current_metric' not in st.session_state:
    st.session_state.current_metric = 'weight'

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🧭 Control Dashboard")
    st.markdown("Configure routing parameters:")
    st.divider()
    
    service_mode = st.selectbox("Select Service Mode", ["Optimization Service (Smart Routes)", "Live Vehicle Tracking"])
    
    source = st.selectbox("📍 From Station", list(nodes_coords.keys()))
    target = st.selectbox("🎯 To Station", list(nodes_coords.keys()), index=2)
    
    opt_type = st.radio("⚙️ Optimize Based On:", ["Minimum Distance (Weight)", "Minimum Cost (Fare)"])
    metric = 'weight' if 'Distance' in opt_type else 'fare'
    
    st.markdown("<br>", unsafe_allow_html=True)
    find_btn = st.button("🚀 Suggest Best Route", type="primary")
    
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

# --- MAIN LAYOUT ---
# Display Route Summary inside a beautiful custom card if calculated
if st.session_state.calculated_path:
    st.markdown(f"""
        <div class="metric-container">
            <h4>💡 Optimal Route Found Successfully</h4>
            <p style="font-size: 16px; font-weight: bold; color: #333;">Path: {' ➔ '.join(st.session_state.calculated_path)}</p>
            <p style="font-size: 15px; color: #555;">Total {"Distance" if st.session_state.current_metric == 'weight' else "Cost"}: <b>{st.session_state.total_cost} {"km" if st.session_state.current_metric == 'weight' else "BDT"}</b></p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("### 🗺️ Geographic Transit Map & Direction")

# Initialize Folium Map centered at Dhaka
m = folium.Map(location=[23.7800, 90.4000], zoom_start=12, tiles="OpenStreetMap")

# Draw Route Line and Markers using session state path
if st.session_state.calculated_path:
    path_coords = []
    for node in st.session_state.calculated_path:
        coords = nodes_coords[node]
        path_coords.append(coords)
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
st_folium(m, use_container_width=True, height=540)
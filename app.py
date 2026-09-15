import streamlit as st
import pandas as pd
import networkx as nx
import folium
from streamlit_folium import st_folium
import random

# Page Configuration
st.set_page_config(
    page_title="Smart Public Transportation Route Planner with Traffic",
    page_icon="🚍",
    layout="wide"
)

# Advanced Custom CSS for Modern UI
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
    }
    .stButton>button:hover {
        background-color: #218838;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("# 🚍 Smart Route Planner & Live Traffic Tracker")
st.markdown("##### *Shortest Path Optimization with Real-Time Traffic Congestion Analysis*")
st.markdown("---")

# Load Dynamic Graph & Station Coordinates from CSV File
@st.cache_data
def load_transit_data():
    try:
        df = pd.read_csv("stations.csv")
    except Exception:
        # Fallback dummy data if file is missing
        data = {
            'source': ['Uttara', 'Airport', 'Banani', 'Farmgate'],
            'target': ['Airport', 'Banani', 'Farmgate', 'Shahbagh'],
            'weight': [3.0, 5.5, 4.0, 2.5],
            'fare': [15, 20, 20, 15],
            'lat1': [23.8759, 23.8450, 23.7937, 23.7570],
            'lon1': [90.3795, 90.4003, 90.4066, 90.3900],
            'lat2': [23.8450, 23.7937, 23.7570, 23.7380],
            'lon2': [90.4003, 90.4066, 90.3900, 90.3944]
        }
        df = pd.DataFrame(data)
        
    graph = nx.Graph()
    coords = {}
    
    for _, row in df.iterrows():
        u, v = row['source'], row['target']
        graph.add_edge(u, v, weight=row['weight'], fare=row['fare'])
        coords[u] = (row['lat1'], row['lon1'])
        coords[v] = (row['lat2'], row['lon2'])
        
    return graph, coords

G, nodes_coords = load_transit_data()

# Initialize Session State
if 'calculated_path' not in st.session_state:
    st.session_state.calculated_path = []
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0
if 'current_metric' not in st.session_state:
    st.session_state.current_metric = 'weight'

# --- TRAFFIC SIMULATION FUNCTION ---
def get_traffic_status():
    conditions = [
        {"status": "🟢 Smooth Flow (No Jam)", "multiplier": 1.0, "color": "green", "line_color": "#28a745"},
        {"status": "🟡 Moderate Traffic (Medium Jam)", "multiplier": 1.4, "color": "orange", "line_color": "#ffc107"},
        {"status": "🔴 Heavy Traffic Jam!", "multiplier": 2.2, "color": "red", "line_color": "#dc3545"}
    ]
    return random.choice(conditions)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### 🧭 Control Dashboard")
    st.markdown(f"Loaded **{len(nodes_coords)} Stations**.")
    st.divider()
    
    service_mode = st.selectbox("Select Service Mode", ["Optimization Service (Smart Routes)", "Live Vehicle Tracking"])
    
    station_list = sorted(list(nodes_coords.keys()))
    source = st.selectbox("📍 From Station", station_list)
    target = st.selectbox("🎯 To Station", station_list, index=min(2, len(station_list)-1))
    
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
                st.session_state.traffic_info = get_traffic_status()
            except Exception:
                st.error("No path exists between selected stations!")
                st.session_state.calculated_path = []

# --- MAIN LAYOUT ---
if st.session_state.calculated_path:
    traffic = st.session_state.traffic_info
    est_time = round(st.session_state.total_cost * traffic['multiplier'] * 4, 1)
    
    st.markdown(f"""
        <div class="metric-container">
            <h4>💡 Optimal Route & Traffic Analysis</h4>
            <p style="font-size: 16px; font-weight: bold; color: #333;">Path: {' ➔ '.join(st.session_state.calculated_path)}</p>
            <p style="font-size: 15px; color: #555;">Total Distance: <b>{st.session_state.total_cost} km</b></p>
            <p style="font-size: 15px; color: {traffic['color']};"><b>Live Traffic Status: {traffic['status']}</b></p>
            <p style="font-size: 15px; color: #333;">Estimated Travel Time: <b>~{est_time} minutes</b></p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("### 🗺️ Geographic Transit Map & Live Direction")

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
    
    # Dynamic line color based on traffic (Green = Smooth, Orange = Moderate, Red = Heavy Jam)
    line_color = st.session_state.traffic_info['line_color']
    
    folium.PolyLine(
        path_coords, 
        color=line_color, 
        weight=7,         
        opacity=0.9       
    ).add_to(m)
else:
    for node, coords in nodes_coords.items():
        folium.Marker(
            coords, 
            popup=node, 
            tooltip=node,
            icon=folium.Icon(color="gray", icon="info-sign")
        ).add_to(m)
        
# Render map cleanly inside Streamlit
st_folium(m, use_container_width=True, height=540)
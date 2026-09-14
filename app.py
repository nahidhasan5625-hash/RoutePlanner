import streamlit as st
import networkx as nx
import time

st.set_page_config(page_title="Public Transportation Route Planner", layout="wide")

st.title("🚌 Public Transportation Route Planner")
st.markdown("*(Compute shortest paths, suggest optimized routes, and track vehicle positions)*")

st.sidebar.header("System Modules")
module = st.sidebar.selectbox("Select Service", [
    "Route Planner Service (Shortest Path)", 
    "Optimization Service (Smart Routes)", 
    "Vehicle Tracking Service"
])

G = nx.Graph()
G.add_edge('Uttara', 'Airport', weight=3.0, fare=15)
G.add_edge('Airport', 'Banani', weight=6.0, fare=25)
G.add_edge('Banani', 'Farmgate', weight=4.0, fare=20)
G.add_edge('Farmgate', 'Shahbagh', weight=2.5, fare=15)
G.add_edge('Uttara', 'Banani', weight=8.0, fare=35)

if module == "Route Planner Service (Shortest Path)":
    st.subheader("📍 Route Planner Service - Compute Shortest Paths")
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Starting Point", list(G.nodes()))
    with col2:
        target = st.selectbox("Destination", list(G.nodes()))
        
    if st.button("Compute Shortest Path"):
        try:
            path = nx.shortest_path(G, source=source, target=target, weight='weight')
            distance = nx.shortest_path_length(G, source=source, target=target, weight='weight')
            st.success(f"**Optimal Path:** {' ➔ '.join(path)}")
            st.metric(label="Total Distance", value=f"{distance} km")
        except:
            st.error("No path found between selected locations.")

elif module == "Optimization Service (Smart Routes)":
    st.subheader("⚡ Optimization Service - Suggest Optimized Routes")
    source = st.selectbox("From", list(G.nodes()), key="opt_src")
    target = st.selectbox("To", list(G.nodes()), key="opt_dst")
    
    optimize_by = st.radio("Optimize Based On:", ["Minimum Distance (Weight)", "Minimum Cost (Fare)"])
    
    if st.button("Suggest Best Route"):
        weight_metric = 'weight' if 'Distance' in optimize_by else 'fare'
        path = nx.shortest_path(G, source=source, target=target, weight=weight_metric)
        total_val = nx.shortest_path_length(G, source=source, target=target, weight=weight_metric)
        
        st.info(f"Recommended Route via Optimization: {' ➔ '.join(path)}")
        unit = "km" if 'Distance' in optimize_by else "BDT"
        st.metric(label=f"Total {optimize_by.split()[1]}", value=f"{total_val} {unit}")

elif module == "Vehicle Tracking Service":
    st.subheader("🚍 Real-time Vehicle Position Tracking Simulation")
    route_simulation = st.selectbox("Select Active Route", ["Uttara ➔ Shahbagh"])
    
    if st.button("Start Live Tracking Simulation"):
        path_nodes = ['Uttara', 'Airport', 'Banani', 'Farmgate', 'Shahbagh']
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, node in enumerate(path_nodes):
            status_text.text(f"Vehicle currently at: {node} 🟢")
            progress_bar.progress((i + 1) * 20)
            time.sleep(1)
            
        st.success("Vehicle reached the final destination successfully!")
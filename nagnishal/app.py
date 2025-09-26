import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from pathfinding import CampusPathfinder
from gemini_integration import GeminiAssistant

# Load environment variables from .env file
try:
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass  # .env file is optional

# Page configuration
st.set_page_config(
    page_title="CyberNav: Campus Route AI",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cyberpunk Dark Mode CSS styling
st.markdown("""
<style>
    /* Global dark theme */
    .stApp {
        background-color: #0a0f18;
        color: #00ffff;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #0a0f18;
        color: #00ffff;
    }
    
    /* Header styling - Cyberpunk neon */
    .main-header {
        background: linear-gradient(135deg, #0a0f18 0%, #1a1a2e 50%, #16213e 100%);
        border: 2px solid #00ffff;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(0, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.2), transparent);
        animation: cyberpunk-glow 3s infinite;
    }
    
    @keyframes cyberpunk-glow {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .main-header h1 {
        color: #00ffff;
        margin: 0;
        font-weight: 900;
        font-size: 3rem;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 3px;
        position: relative;
        z-index: 2;
    }
    
    .main-header p {
        color: #ff00ff;
        margin: 1rem 0 0 0;
        font-size: 1.2rem;
        text-shadow: 0 0 10px rgba(255, 0, 255, 0.6);
        position: relative;
        z-index: 2;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a2e;
        border-radius: 10px;
        border: 1px solid #00ffff;
        padding: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #00ffff;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 1.5rem;
        margin: 0 0.25rem;
        border: 1px solid transparent;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(0, 255, 255, 0.1);
        border-color: #00ffff;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 255, 255, 0.2) !important;
        color: #ffffff !important;
        border-color: #00ffff !important;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5) !important;
    }
    
    /* Containers with neon glow */
    .map-container, .info-panel, .ai-container {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00ffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3), inset 0 0 10px rgba(0, 255, 255, 0.1);
        position: relative;
    }
    
    .map-container h3, .info-panel h3, .ai-container h3 {
        color: #00ffff;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
        margin-bottom: 1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling - Cyberpunk neon */
    .stButton > button {
        background: linear-gradient(135deg, #ff00ff 0%, #00ffff 100%);
        color: #000000;
        border: 2px solid #00ffff;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ffff 0%, #ff00ff 100%);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.8), 0 0 35px rgba(255, 0, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Metric cards - Cyberpunk style */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #00ffff;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
    }
    
    div[data-testid="metric-container"] label {
        color: #ff00ff !important;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(255, 0, 255, 0.6);
    }
    
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #00ffff !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #1a1a2e;
        border: 1px solid #00ffff;
        border-radius: 8px;
        color: #00ffff;
    }
    
    .stSelectbox label {
        color: #ff00ff !important;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(255, 0, 255, 0.6);
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid #00ffff;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    }
    
    /* Chat styling */
    .stChatMessage {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #00ffff;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(0, 255, 0, 0.1);
        border: 1px solid #00ff00;
        border-radius: 8px;
        color: #00ff00;
    }
    
    .stError {
        background-color: rgba(255, 0, 0, 0.1);
        border: 1px solid #ff0040;
        border-radius: 8px;
        color: #ff0040;
    }
    
    .stWarning {
        background-color: rgba(255, 255, 0, 0.1);
        border: 1px solid #ffff00;
        border-radius: 8px;
        color: #ffff00;
    }
    
    .stInfo {
        background-color: rgba(0, 255, 255, 0.1);
        border: 1px solid #00ffff;
        border-radius: 8px;
        color: #00ffff;
    }
    
    /* Text colors */
    .stMarkdown, .stText, p, div {
        color: #00ffff;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ff00ff !important;
        text-shadow: 0 0 10px rgba(255, 0, 255, 0.6);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1a1a2e;
        border: 1px solid #00ffff;
        color: #00ffff;
        border-radius: 8px;
    }
    
    .stChatInput > div > div > input {
        background-color: #1a1a2e;
        border: 2px solid #00ffff;
        color: #00ffff;
        border-radius: 25px;
    }
    
    /* Sidebar (minimized) */
    .css-1d391kg {
        background-color: #0a0f18;
        border-right: 1px solid #00ffff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize pathfinder and Gemini assistant
@st.cache_resource
def initialize_pathfinder():
    return CampusPathfinder("attached_assets/map_1758707724808.osm")

@st.cache_resource
def initialize_gemini():
    try:
        # Check for API key in environment variables (set by Replit Secrets)
        if not os.environ.get("GEMINI_API_KEY"):
            st.warning("🔧 AI Assistant unavailable: GEMINI_API_KEY not configured")
            return None
        return GeminiAssistant()
    except Exception as e:
        st.error(f"Failed to initialize AI Assistant: {str(e)}")
        return None

try:
    pathfinder = initialize_pathfinder()
    gemini = initialize_gemini()
    
    # Cyberpunk header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 CyberNav: Campus Route AI</h1>
        <p>Neural pathfinding matrix with quantum AI assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for the new layout
    tab1, tab2 = st.tabs(["🗺️ Route Planner", "🧪 AI & Analysis"])
    
    # Tab 1: Route Planner
    with tab1:
        # Route planning controls (moved from sidebar)
        st.markdown("""
        <div class="map-container">
            <h3>🎯 Neural Route Configuration</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_control1, col_control2, col_control3 = st.columns(3)
        
        with col_control1:
            st.markdown("**Select Journey Points**")
            locations = list(pathfinder.POIS.keys())
            start_location = st.selectbox("🚀 Start Location", locations, index=0, help="Choose your starting point")
            
        with col_control2:
            end_location = st.selectbox("🎯 Destination", locations, index=1, help="Choose your destination")
            
        with col_control3:
            algorithm = st.selectbox(
                "⚡ Pathfinding Algorithm",
                ["A*", "A* (Euclidean)", "A* (Manhattan)", "A* (Combined)", "BFS", "DFS", "UCS"],
                index=0,
                help="Choose the pathfinding algorithm. A* variants are recommended for optimal routes."
            )
        
        # Find path button
        st.markdown("<br>", unsafe_allow_html=True)
        run_pathfinding = st.button("🔥 FIND OPTIMAL PATH", type="primary", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Map and route information side by side
        col1, col2 = st.columns([2.2, 1], gap="large")
        
        with col1:
            st.markdown("""
            <div class="map-container">
                <h3>🗺️ Interactive Neural Map</h3>
            """, unsafe_allow_html=True)
            
            # Initialize map display
            if 'current_map' not in st.session_state:
                st.session_state['current_map'] = pathfinder.create_base_map()
            
            # Handle pathfinding request
            if run_pathfinding:
                try:
                    with st.spinner(f"Neural processing using {algorithm}..."):
                        result = pathfinder.find_path(start_location, end_location, algorithm)
                        st.session_state['current_map'] = result['map']
                        st.session_state['path_metrics'] = result['metrics']
                        st.session_state['algorithm_used'] = algorithm
                        
                    st.success(f"⚡ Optimal path calculated using {algorithm} algorithm!")
                except Exception as e:
                    st.error(f"🚨 Neural pathway error: {str(e)}")
            
            # Display map
            if st.session_state['current_map']:
                map_data = st_folium(
                    st.session_state['current_map'],
                    width=None,
                    height=500,
                    returned_objects=["last_clicked"]
                )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-panel">
                <h3>📊 Route Neural Data</h3>
            """, unsafe_allow_html=True)
            
            # Route metrics display
            if 'path_metrics' in st.session_state:
                metrics = st.session_state['path_metrics']
                algorithm_used = st.session_state.get('algorithm_used', 'Unknown')
                
                # Metrics in organized columns
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("⚡ Algorithm", algorithm_used)
                    st.metric("📏 Distance", f"{metrics['distance']:.0f}m")
                with col_m2:
                    st.metric("⏱️ Time", f"{metrics['time']:.1f} min")
                    st.metric("🔍 Explored", f"{metrics['nodes_explored']:,}")
                
                # Route details
                st.markdown("---")
                st.markdown("**🛸 Journey Neural Path**")
                
                start_info = pathfinder.get_location_info(metrics['start_location'])
                end_info = pathfinder.get_location_info(metrics['end_location'])
                
                st.markdown(f"""
**From:** {start_info['name']}  
**To:** {end_info['name']}  
**Status:** 🎯 Optimal neural path activated
                """)
            else:
                st.markdown("""
                <div style="padding: 2rem; text-align: center; color: #00ffff;">
                    <h4>🤖 Select Neural Route</h4>
                    <p>Configure start and destination coordinates, then activate 'FIND OPTIMAL PATH' to initialize neural pathfinding matrix.</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 2: AI & Analysis
    with tab2:
        col_ai1, col_ai2 = st.columns([1, 1], gap="large")
        
        with col_ai1:
            # AI Chat Interface
            st.markdown("""
            <div class="ai-container">
                <h3>🤖 AI Campus Neural Assistant</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize chat history
            if 'messages' not in st.session_state:
                st.session_state.messages = []

            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input with proper error handling
            if gemini is None:
                st.info("🔧 AI Neural Network is currently offline. Please configure GEMINI_API_KEY to activate.")
                st.chat_input("AI Neural Assistant offline...", disabled=True)
            else:
                user_query = st.chat_input("Query the campus neural network...")
                
                if user_query:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_query})
                    with st.chat_message("user"):
                        st.markdown(user_query)
                    
                    # Generate AI response
                    with st.chat_message("assistant"):
                        with st.spinner("🧠 Neural processing..."):
                            try:
                                # Get AI response
                                response = gemini.get_response(user_query)
                                
                                # Display the response
                                st.markdown(response["text"])
                                
                                # Add assistant response to chat history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": response["text"]
                                })
                                
                            except Exception as e:
                                st.error("🚨 Neural network error. Please recalibrate your query.")
                                print(f"Error: {str(e)}")
            
            # Chat history display
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            
            if len(st.session_state.chat_history) > 0:
                st.subheader("💾 Recent Neural Conversations")
                for chat in st.session_state.chat_history[-3:]:
                    with st.expander(f"Q: {chat['question'][:50]}..."):
                        st.write(f"**Neural Response:** {chat['answer']}")
        
        with col_ai2:
            # Performance Analysis
            st.markdown("""
            <div class="ai-container">
                <h3>📈 Performance Neural Analysis</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔥 Compare Algorithms", help="Analyze algorithm performance matrix"):
                    st.session_state['run_comparison'] = True
            
            with col_b:
                if st.button("⚡ Compare Heuristics", help="Analyze A* heuristic neural variants"):
                    st.session_state['run_heuristic_comparison'] = True
    
    # Algorithm comparison results
    if 'run_comparison' in st.session_state:
        st.markdown("---")
        st.subheader("🔥 Algorithm Performance Neural Matrix")
        
        with st.spinner("🧠 Running neural algorithm comparison..."):
            try:
                comparison_results = pathfinder.compare_algorithms()
                
                # Display results table
                df = pd.DataFrame(comparison_results)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=False
                )
                
                # Performance insights
                st.subheader("⚡ Neural Performance Insights")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fastest_algo = df.loc[df['Average Distance (m)'].idxmin(), 'Algorithm']
                    st.metric("🏆 Shortest Neural Path", str(fastest_algo))
                
                with col2:
                    least_explored = df.loc[df['Average Nodes Explored'].idxmin(), 'Algorithm']
                    st.metric("⚡ Most Efficient Neural", str(least_explored))
                
                with col3:
                    most_explored = df.loc[df['Average Nodes Explored'].idxmax(), 'Algorithm']
                    st.metric("🔍 Most Thorough Neural", str(most_explored))
                
                del st.session_state['run_comparison']
                
            except Exception as e:
                st.error(f"🚨 Neural comparison error: {str(e)}")
    
    # Heuristic comparison results
    if 'run_heuristic_comparison' in st.session_state:
        st.markdown("---")
        st.subheader("⚡ A* Heuristic Neural Comparison")
        
        with st.spinner("🧠 Running heuristic neural analysis..."):
            try:
                heuristic_results = pathfinder.compare_heuristics()
                
                # Display results table
                df_heuristic = pd.DataFrame(heuristic_results)
                st.dataframe(
                    df_heuristic,
                    use_container_width=True,
                    hide_index=False
                )
                
                # Heuristic insights
                st.subheader("🔬 Neural Heuristic Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    best_heuristic = df_heuristic.loc[df_heuristic['Average Distance (m)'].idxmin(), 'Heuristic Type']
                    st.metric("🎯 Best Neural Distance", str(best_heuristic))
                
                with col2:
                    most_efficient = df_heuristic.loc[df_heuristic['Average Nodes Explored'].idxmin(), 'Heuristic Type']
                    st.metric("⚡ Most Efficient Neural", str(most_efficient))
                
                with col3:
                    best_efficiency = df_heuristic.loc[df_heuristic['Efficiency Score'].idxmax(), 'Heuristic Type']
                    st.metric("🏆 Best Neural Efficiency", str(best_efficiency))
                
                # Detailed analysis
                st.subheader("🔬 Detailed Neural Heuristic Analysis")
                
                st.write("**Neural Key Insights:**")
                st.write("• **Euclidean Neural Distance**: Calculates direct neural pathway between coordinates")
                st.write("• **Manhattan Neural Distance**: Sum of horizontal and vertical neural pathways")
                st.write("• **Combined Neural Heuristic**: Weighted neural combination (70% Euclidean + 30% Manhattan)")
                st.write("• **Neural Efficiency Score**: Distance per node explored (higher = better path quality per neural exploration)")
                
                del st.session_state['run_heuristic_comparison']
                
            except Exception as e:
                st.error(f"🚨 Neural heuristic comparison error: {str(e)}")
    
    # Cyberpunk footer
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #00ffff;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
    ">
        <h4 style="color: #00ffff; margin-bottom: 0.5rem; text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);">CyberNav: Campus Route AI</h4>
        <p style="color: #ff00ff; margin: 0; text-shadow: 0 0 10px rgba(255, 0, 255, 0.6);">Powered by Neural Pathfinding Algorithms, Quantum OpenStreetMap & Gemini Neural AI</p>
        <p style="color: #00ffff; font-size: 0.9rem; margin-top: 0.5rem;">Advanced neural routing matrix for cybernetic educational institutions</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"🚨 Neural System Error: {str(e)}")
    st.info("Please ensure the OSM neural data file is properly loaded and all neural dependencies are installed.")
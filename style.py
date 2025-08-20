import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Import Enterprise Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global App Styling with Music Background */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: #f8fafc;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.05) 0%, transparent 50%);
        position: relative;
    }
    
    .stApp::before {
        content: '🎵 🎶 🎼 🎹 🎸 🥁 🎻 🎤 🎺 🎷 🪈 🎧';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        font-size: 2rem;
        opacity: 0.02;
        pointer-events: none;
        z-index: -1;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
        align-items: center;
        animation: float 20s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(2deg); }
    }
    
    /* Enterprise Header */
    .enterprise-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-bottom: 3px solid #0ea5e9;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.2);
    }
    
    .enterprise-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .enterprise-header .subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Dashboard Grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Navigation Cards */
    .nav-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .nav-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    
    .nav-card:hover::before {
        transform: scaleX(1);
    }
    
    .nav-card-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
        background: linear-gradient(135deg, #3b82f6, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .nav-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .nav-card-desc {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.5;
    }
    
    /* Metrics Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981, #06b6d4);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1rem 0 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.875rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
        text-transform: none;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Form Elements */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 0.75rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    /* Data Tables */
    .dataframe {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe th {
        background: #f8fafc;
        font-weight: 600;
        color: #374151;
        padding: 1rem;
    }
    
    .dataframe td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #f1f5f9;
    }
    
    /* Status Badges */
    .status-active {
        background: #dcfce7;
        color: #166534;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid #bbf7d0;
    }
    
    .status-expired {
        background: #fef2f2;
        color: #dc2626;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid #fecaca;
    }
    
    /* Alert Components */
    .alert-success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .alert-warning {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        color: #92400e;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .alert-danger {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Section Headers */
    .section-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Page Container */
    .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    
    /* Loading States */
    .stSpinner {
        border-color: #3b82f6;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-grid {
            grid-template-columns: 1fr;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .enterprise-header h1 {
            font-size: 1.5rem;
        }
    }
    
    </style>
    """, unsafe_allow_html=True)

def get_instrument_emoji(instrument):
    emoji_map = {
        "Keyboard": "🎹",
        "Piano": "🎹", 
        "Guitar": "🎸",
        "Drums": "🥁",
        "Violin": "🎻",
        "Flute": "🪈",
        "Carnatic Vocals": "🎤",
        "Hindustani Vocals": "🎤",
        "Western Vocals": "🎤"
    }
    return emoji_map.get(instrument, "🎵")

def display_header(title, subtitle="Professional Music Education Management"):
    st.markdown(f"""
    <div class="enterprise-header">
        <h1>🎵 {title}</h1>
        <div class="subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def display_metric_card(title, value, icon="📊", color="#3b82f6"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="color: {color};">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """, unsafe_allow_html=True)

def display_section_header(title):
    st.markdown(f"""
    <div class="section-header">
        <h2 class="section-title">{title}</h2>
    </div>
    """, unsafe_allow_html=True)
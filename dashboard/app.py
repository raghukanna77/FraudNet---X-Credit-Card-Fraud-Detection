"""
Streamlit Dashboard for FraudNet-X
Interactive visualization and monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.config import Config


# Page configuration
st.set_page_config(
    page_title="FraudNet-X Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-critical {
        color: #d32f2f;
        font-weight: bold;
    }
    .risk-high {
        color: #f57c00;
        font-weight: bold;
    }
    .risk-medium {
        color: #fbc02d;
        font-weight: bold;
    }
    .risk-low {
        color: #388e3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"


def check_api_health(api_url):
    """Check if API is healthy"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        return response.status_code == 200, response.json()
    except:
        return False, None


def predict_transaction(api_url, transaction_data):
    """Send transaction to API for prediction"""
    try:
        response = requests.post(
            f"{api_url}/predict",
            json=transaction_data,
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None


def create_risk_gauge(risk_score):
    """Create risk gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Score"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 60], 'color': "yellow"},
                {'range': [60, 85], 'color': "orange"},
                {'range': [85, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=300)
    return fig


def create_risk_distribution(transactions):
    """Create risk distribution chart"""
    if not transactions:
        return None
    
    df = pd.DataFrame(transactions)
    
    risk_counts = df['risk_level'].value_counts()
    
    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Risk Distribution",
        color=risk_counts.index,
        color_discrete_map={
            'Low': 'green',
            'Medium': 'yellow',
            'High': 'orange',
            'Critical': 'red'
        }
    )
    fig.update_layout(height=400)
    return fig


def create_time_series(transactions):
    """Create time series of risk scores"""
    if not transactions:
        return None
    
    df = pd.DataFrame(transactions)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['risk_score'],
        mode='lines+markers',
        name='Risk Score',
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        title="Risk Score Over Time",
        xaxis_title="Time",
        yaxis_title="Risk Score",
        height=400
    )
    return fig


# Main dashboard
def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ FraudNet-X Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Adaptive Real-Time Cost-Sensitive Explainable Graph-Temporal Hybrid Fraud Detection System**")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    api_url = st.sidebar.text_input("API URL", st.session_state.api_url)
    st.session_state.api_url = api_url
    
    # Check API health
    is_healthy, health_data = check_api_health(api_url)
    
    if is_healthy:
        st.sidebar.success("✅ API Connected")
        if health_data:
            st.sidebar.json(health_data)
    else:
        st.sidebar.error("❌ API Disconnected")
        st.warning("⚠️ Cannot connect to API. Please ensure the API is running.")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Overview", "🔍 Single Transaction", "📈 Batch Analysis", "📉 Monitoring"]
    )
    
    # Overview Page
    if page == "📊 Overview":
        st.header("System Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", len(st.session_state.transactions))
        
        with col2:
            if st.session_state.transactions:
                high_risk = sum(1 for t in st.session_state.transactions if t['risk_level'] in ['High', 'Critical'])
                st.metric("High Risk", high_risk)
            else:
                st.metric("High Risk", 0)
        
        with col3:
            if st.session_state.transactions:
                avg_risk = np.mean([t['risk_score'] for t in st.session_state.transactions])
                st.metric("Avg Risk Score", f"{avg_risk:.2f}")
            else:
                st.metric("Avg Risk Score", "N/A")
        
        with col4:
            if st.session_state.transactions:
                avg_latency = np.mean([t['latency_ms'] for t in st.session_state.transactions])
                st.metric("Avg Latency", f"{avg_latency:.2f} ms")
            else:
                st.metric("Avg Latency", "N/A")
        
        # Charts
        if st.session_state.transactions:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_risk_distribution(st.session_state.transactions)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_time_series(st.session_state.transactions)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent transactions table
            st.subheader("Recent Transactions")
            df = pd.DataFrame(st.session_state.transactions)
            df = df[['transaction_id', 'risk_score', 'risk_level', 'fraud_probability', 'latency_ms']].tail(10)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transactions yet. Go to 'Single Transaction' to make predictions.")
    
    # Single Transaction Page
    elif page == "🔍 Single Transaction":
        st.header("Single Transaction Prediction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Transaction Details")
            
            time_val = st.number_input("Time (seconds)", value=12345.0, format="%.2f")
            amount = st.number_input("Amount ($)", value=100.0, min_value=0.0, format="%.2f")
            
            # V features (simplified input)
            st.write("**V Features (PCA components):**")
            v_features = {}
            
            # Create columns for V features
            v_cols = st.columns(4)
            for i in range(1, 29):
                col_idx = (i-1) % 4
                with v_cols[col_idx]:
                    v_features[f'V{i}'] = st.number_input(
                        f"V{i}",
                        value=0.0,
                        format="%.6f",
                        key=f"v{i}"
                    )
        
        with col2:
            st.subheader("Prediction Result")
            
            if st.button("🔍 Predict Fraud", type="primary"):
                if not is_healthy:
                    st.error("API is not connected!")
                else:
                    # Prepare transaction data
                    transaction_data = {
                        'Time': time_val,
                        'Amount': amount,
                        **v_features
                    }
                    
                    # Make prediction
                    with st.spinner("Analyzing transaction..."):
                        result = predict_transaction(api_url, transaction_data)
                    
                    if result:
                        # Store in session
                        st.session_state.transactions.append(result)
                        
                        # Display result
                        risk_score = result['risk_score']
                        risk_level = result['risk_level']
                        
                        # Risk gauge
                        fig = create_risk_gauge(risk_score)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Risk level with color
                        risk_class = f"risk-{risk_level.lower()}"
                        st.markdown(f'<p class="{risk_class}">Risk Level: {risk_level}</p>', unsafe_allow_html=True)
                        
                        # Metrics
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Fraud Probability", f"{result['fraud_probability']:.2%}")
                        col_b.metric("Confidence", f"{result['confidence']:.2%}")
                        col_c.metric("Latency", f"{result['latency_ms']:.2f} ms")
                        
                        # Recommendation
                        rec = result['recommendation']
                        st.info(f"**Recommendation:** {rec['action']}")
                        st.write(rec['description'])
                        
                        # Component scores
                        with st.expander("Component Scores"):
                            st.json(result)
    
    # Batch Analysis Page
    elif page == "📈 Batch Analysis":
        st.header("Batch Transaction Analysis")
        
        st.write("Upload a CSV file with transactions for batch analysis")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.write(f"Loaded {len(df)} transactions")
            st.dataframe(df.head())
            
            if st.button("Analyze Batch"):
                st.warning("Batch analysis requires API batch endpoint (not implemented in this demo)")
                # In production, implement batch endpoint and process here
    
    # Monitoring Page
    elif page == "📉 Monitoring":
        st.header("System Monitoring")
        
        # Drift detection status
        st.subheader("Drift Detection")
        
        try:
            response = requests.get(f"{api_url}/metrics")
            if response.status_code == 200:
                metrics = response.json()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Predictions", metrics.get('total_requests', 0))
                
                with col2:
                    st.metric("Avg Latency", f"{metrics.get('average_latency_ms', 0):.2f} ms")
                
                drift_status = metrics.get('drift_status')
                if drift_status:
                    st.json(drift_status)
                    
                    if drift_status.get('total_drifts_detected', 0) > 0:
                        st.warning(f"⚠️ {drift_status['total_drifts_detected']} concept drifts detected!")
        except:
            st.error("Could not fetch metrics from API")
        
        # Model info
        st.subheader("Model Information")
        try:
            response = requests.get(f"{api_url}/model-info")
            if response.status_code == 200:
                model_info = response.json()
                st.json(model_info)
        except:
            st.error("Could not fetch model info from API")
        
        # Auto-refresh
        if st.checkbox("Auto-refresh (every 5 seconds)"):
            time.sleep(5)
            st.rerun()


if __name__ == "__main__":
    main()

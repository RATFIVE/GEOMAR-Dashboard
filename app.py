from Layout import StreamlitApp
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import sys
import streamlit as st
st.set_page_config(layout="wide", page_title="Application", page_icon=":shark:")



def run_streamlit():
    subprocess.run([sys.executable, "-m", "streamlit", "run", "Layout.py"])

if __name__ == '__main__':
    run_streamlit()
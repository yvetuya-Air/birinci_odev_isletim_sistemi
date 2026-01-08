import streamlit as st
import pandas as pd
import threading
import tempfile
import os
import base64
from algos.fcfs_optimized import FCFS
from algos.pjf_preemptive_optimized import PJF_Preemptive 
from algos.rr_optimized import RR

# --- HELPER FUNCTION FOR HTML DOWNLOADS ---
def get_download_link(file_path, link_text):
    """Generates a link to download the file without refreshing the Streamlit page."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        filename = os.path.basename(file_path)
        # HTML with some basic styling to make it look like a button
        html = f'''
            <a href="data:text/plain;base64,{b64}" download="{filename}" style="text-decoration: none;">
                <div style="
                    display: inline-block;
                    padding: 0.5em 1em;
                    color: white;
                    background-color: #ff4b4b;
                    border-radius: 0.5rem;
                    text-align: center;
                    font-weight: 500;
                    border: 1px solid #ff4b4b;
                    transition: opacity 0.3s;
                    cursor: pointer;
                    width: 100%;">
                    {link_text}
                </div>
            </a>
        '''
        return html
    except Exception as e:
        return f"File error: {e}"

st.title("Sample App")
uploaded_file = st.file_uploader("Upload your process CSV file", type=["csv"])

if uploaded_file:
    temp_dir = tempfile.gettempdir() 
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Initialize session state for stats and results
    if 'sim_results' not in st.session_state:
        st.session_state.sim_results = None

    if st.button("Run Simulation"):
        # Create instances
        fcfs = FCFS(temp_path)
        pjf_p = PJF_Preemptive(temp_path)
        rr = RR(temp_path, 2)

        # Setup Threads
        t1 = threading.Thread(target=fcfs.main)
        t2 = threading.Thread(target=pjf_p.main)
        t3 = threading.Thread(target=rr.main)

        with st.spinner("Simulations running..."):
            t1.start()
            t2.start()
            t3.start()
            t1.join() 
            t2.join() 
            t3.join()

        # Trigger file generation
        fcfs.export_timeline()
        pjf_p.export_timeline()
        rr.export_timeline()

        # Filenames
        base_name = os.path.splitext(uploaded_file.name)[0]
        f_fcfs = f"{base_name}_FCFS.txt"
        f_pjf = f"{base_name}_PJF.txt"
        f_rr = f"{base_name}_RR.txt"

        # Save objects and paths to session state so they persist
        st.session_state.sim_results = {
            "fcfs": {"stats": fcfs.bekleme_stats(), "file": f_fcfs},
            "pjf": {"stats": pjf_p.bekleme_stats(), "file": f_pjf},
            "rr": {"stats": rr.bekleme_stats(), "file": f_rr}
        }

    # --- DISPLAY LOGIC (PERSISTENT) ---
    if st.session_state.sim_results:
        res = st.session_state.sim_results
        
        st.divider()
        st.subheader("İndirme Raporları")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            if os.path.exists(res["fcfs"]["file"]):
                st.markdown(get_download_link(res["fcfs"]["file"], "FCFS Raporu"), unsafe_allow_html=True)

        with col2:
            if os.path.exists(res["pjf"]["file"]):
                st.markdown(get_download_link(res["pjf"]["file"], "PJF Raporu"), unsafe_allow_html=True)

        with col3:
            if os.path.exists(res["rr"]["file"]):
                st.markdown(get_download_link(res["rr"]["file"], "RR Raporu"), unsafe_allow_html=True)

        st.subheader("Bekleme Statistics")
        df_bekleme = pd.DataFrame({
            'FCFS': res["fcfs"]["stats"],
            'PJF': res["pjf"]["stats"],
            'RR': res["rr"]["stats"]
        }).T
        st.table(df_bekleme)
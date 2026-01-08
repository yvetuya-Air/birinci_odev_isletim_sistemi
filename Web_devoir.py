import streamlit as st
import pandas as pd
import threading
import tempfile
import os
import zipfile
from algos.fcfs_optimized import FCFS
from algos.pjf_preemptive_optimized import PJF_Preemptive 
from algos.rr_optimized import RR
from algos.pjf_optimized import PJF
from algos.sjf_preemptive_optimized import SJF_Preemptive 
from algos.sjf_optimized import SJF  


st.title("CPU Zamanlama Odev1")
uploaded_file = st.file_uploader("CSV file yukleyin", type=["csv", "txt"])
quantum = st.number_input("RR Quantum degeri", min_value=1, value=2, step=1)

def zip_files(file_list, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in file_list:
            zipf.write(file)

if uploaded_file:
    temp_dir = tempfile.gettempdir() 
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Run Algoritmalarin hepsi"):
        fcfs = FCFS(temp_path)
        t1 = threading.Thread(target=fcfs.main)
        pjf_p = PJF_Preemptive(temp_path)
        t2 = threading.Thread(target=pjf_p.main)
        rr = RR(temp_path, 2)
        t3 = threading.Thread(target=rr.main)
        pjf = PJF(temp_path)
        t4 = threading.Thread(target=pjf.main)
        sjp_p = SJF_Preemptive(temp_path)
        t5 = threading.Thread(target=sjp_p.main)
        sjf = SJF(temp_path)
        t6 = threading.Thread(target=sjf.main)


        with st.spinner("Simulation running..."):

            t1.start()
            t2.start()
            t3.start()
            t4.start()  
            t5.start()
            t6.start()
            t6.join()
            t5.join()
            t4.join()
            t3.join()
            t1.join() 
            t2.join()


        output_filename_FCFS = f"{os.path.splitext(uploaded_file.name)[0]}_FCFS.txt"
        output_filename_PJF_p = f"{os.path.splitext(uploaded_file.name)[0]}_PJF_Preemptive.txt"
        output_filename_RR = f"{os.path.splitext(uploaded_file.name)[0]}_RR.txt"
        output_filename_PJF = f"{os.path.splitext(uploaded_file.name)[0]}_PJF.txt"
        output_filename_SJF_p = f"{os.path.splitext(uploaded_file.name)[0]}_SJF_Preemptive.txt"
        output_filename_SJF = f"{os.path.splitext(uploaded_file.name)[0]}_SJF.txt"

        fcfs.export_timeline()
        pjf_p.export_timeline() 
        rr.export_timeline()
        pjf.export_timeline()
        sjp_p.export_timeline()
        sjf.export_timeline()

        zip_files([output_filename_FCFS, output_filename_PJF_p, output_filename_RR, 
                   output_filename_PJF, output_filename_SJF_p, output_filename_SJF], "simulation_results.zip")

        st.success("Simulations complete!")

        if os.path.exists("simulation_results.zip"):
            with open("simulation_results.zip", "rb") as f:
                st.download_button(
                    label="Zamanlama Raporlarini Indir (ZIP)",
                    data=f,
                    file_name="Zamanmama_results.zip",
                    mime="text/plain"
                )


        df_bekleme_stats = pd.DataFrame({
            'fcfs' : fcfs.bekleme_stats(),
            'pjf_preemptive' : pjf_p.bekleme_stats(),
            'rr' : rr.bekleme_stats(),
            'pjf' : pjf.bekleme_stats(),
            'sjf_preemptive' : sjp_p.bekleme_stats(),
            'sjf' : sjf.bekleme_stats()}) 

        st.subheader("Bekleme Statistics")
        st.dataframe(df_bekleme_stats)

        df_turnaound_stats = pd.DataFrame({
            'fcfs' : fcfs.turnaound_stats(),
            'pjf_preemptive' : pjf_p.turnaround_stats(),
            'rr' : rr.turnaound_stats(),
            'pjf' : pjf.turnaound_stats(),
            'sjf_preemptive' : sjp_p.turnaround_stats(),
            'sjf' : sjf.turnaound_stats()})

        st.subheader("Tamamlama Statistics") 
        st.dataframe(df_turnaound_stats)

        df_throughput_stats = pd.DataFrame({
            'fcfs' : fcfs.throughput_stats(),
            'pjf_preemptive' : pjf_p.throughput_stats(),
            'rr' : rr.throughput_stats(),
            'pjf' : pjf.throughput_stats(),
            'sjf_preemptive' : sjp_p.throughput_stats(),
            'sjf' : sjf.throughput_stats()})

        st.subheader("Troughput Statistics") 
        st.dataframe(df_throughput_stats)

        df_cpu_utilization_stats = pd.DataFrame({
            'fcfs' : fcfs.calculate_cpu_utilization(),
            'pjf_preemptive' : pjf_p.calculate_cpu_utilization(),
            'rr' : rr.calculate_cpu_utilization(),
            'pjf' : pjf.calculate_cpu_utilization(),
            'sjf_preemptive' : sjp_p.calculate_cpu_utilization(),
            'sjf' : sjf.calculate_cpu_utilization()})

        st.subheader("CPU verimi") 
        st.dataframe(df_cpu_utilization_stats)

        print(rr.turnaound_stats()  )
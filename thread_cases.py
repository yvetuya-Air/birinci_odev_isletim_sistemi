from algos.fcfs_optimized import FCFS
from algos.pjf_preemptive_optimized import PJF_Preemptive
import pandas as pd

import threading

fcfs  = FCFS("test_input.csv")
t1 = threading.Thread(target=fcfs.main)

pjf_preemptive = PJF_Preemptive("test_input.csv")
t2 = threading.Thread(target=pjf_preemptive.main)


t1.start()
t1.join()

t2.start()
t2.join()

print("Simulation complete.")
fcfs.export_timeline()
pjf_preemptive.export_timeline()

bekleme_df = pd.DataFrame({
    "FCFS": fcfs.bekleme_stats(),
    "PJF_Preemptive": pjf_preemptive.bekleme_stats()
})


print(bekleme_df)
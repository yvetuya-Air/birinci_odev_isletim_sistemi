import time
import pandas as pd
import csv

class process:
    def __init__(self, ID, gelme_zamani, islemci_zamani, priority, state):
        self.ID = ID
        self.gz = int(gelme_zamani)
        self.priority = priority
        self.iz = int(islemci_zamani)
        self.state = state

from collections import deque
from pathlib import Path

class RR():
  def __init__(self, path, quantum):
    self.simdi = 0
    self.raporu_stats = []
    self.processes = self.read_csv(path)
    self.quantum = quantum
    self.baglam_degistirme_stats = []
    self.context_stats = []
    self.path = path

  def print_list(liste):
    print([  (p.ID, p.state, p.gz, p.iz) for p in liste])

  def read_csv(self, path):
    process_list = []
    with open(path, 'r') as file:
      reader = csv.reader(file)
      for row in reader:
        process_list.append(tuple(row))
    return  [process(*t,"") for t in process_list[1:] ]

  def export_timeline(self):
        output_path=f"{Path(self.path).stem}_RR.txt"
        try:
            with open(output_path, 'w', newline='') as file:
                writer = csv.writer(file)

                for segment in self.context_stats:
                    line = f"[ {segment['Baslangic']} ] - - {segment['ID']} - - [ {segment['Bitis']} ]"
                    writer.writerow([line])

            print(f"Zamanlama raporu cikti : {output_path}")

        except Exception as e:
            print(f"Error exporting timeline: {e}")

  def bekleme_stats(self):

    process_data = {}

    for segment in self.context_stats:
        pid = segment['ID']
        if pid == 'IDLE':
            continue

        if pid not in process_data:
            process_data[pid] = {
                'Gelis': segment['Gelis'],
                'Bitis': segment['Bitis'],
                'Toplam_Islem': segment['Islem_Suresi']
            }
        else:
            process_data[pid]['Bitis'] = segment['Bitis']
            process_data[pid]['Toplam_Islem'] += segment['Islem_Suresi']

    waiting_times = []
    for pid, data in process_data.items():
        wait = (data['Bitis'] - data['Gelis']) - data['Toplam_Islem']
        waiting_times.append(wait)

    if not waiting_times:
        return {"ortalama": 0, "maksimum": 0}

    return {
        "ortalama": round(sum(waiting_times) / len(waiting_times), 2),
        "maksimum": round(float(max(waiting_times)), 2),
    }

  def turnaound_stats(self):

    process_data = {}

    for segment in self.context_stats:
        pid = segment['ID']
        if pid == 'IDLE':
            continue

        if pid not in process_data:
            process_data[pid] = {
                'Gelis': segment['Gelis'],
                'Bitis': segment['Bitis'],
                'Toplam_Islem': segment['Islem_Suresi']
            }
        else:
            process_data[pid]['Bitis'] = segment['Bitis']
            process_data[pid]['Toplam_Islem'] += segment['Islem_Suresi']

    turnaround_times = []
    for pid, data in process_data.items():
        turnaround = (data['Bitis'] - data['Gelis'])
        turnaround_times.append(turnaround)

    if not turnaround_times:
        return {"ortalama": 0, "maksimum": 0}

    return {
        "ortalama": round(sum(turnaround_times) / len(turnaround_times), 2),
        "maksimum": round(float(max(turnaround_times)), 2),
    }

  def throughput_stats(self, time_limits=[50, 100, 150, 200]):

    completion_times = {}
    for segment in self.context_stats:
        if segment['ID'] != 'IDLE':
            completion_times[segment['ID']] = segment['Bitis']

    final_times = list(completion_times.values())

    throughput_results = {}

    for limit in time_limits:
        count = sum(1 for finish_time in final_times if finish_time <= limit)
        throughput_results[f"T={limit}"] = count

    return throughput_results

  def calculate_cpu_utilization(self, context_switch_time=0.01):
    total_cpu_burst_time = sum(
        s['Islem_Suresi'] for s in self.context_stats if s['ID'] != 'IDLE'
    )

    num_switches = 0
    for i in range(len(self.context_stats) - 1):
        current_id = self.context_stats[i]['ID']
        next_id = self.context_stats[i+1]['ID']
        
        if current_id != next_id:
            num_switches += 1
    total_overhead = num_switches * context_switch_time

    if not self.context_stats:
        return {"cpu_utilization": 0}

    total_elapsed_time = self.context_stats[-1]['Bitis']
    total_time_with_overhead = total_elapsed_time + total_overhead
    cpu_utilization = ( total_cpu_burst_time / total_time_with_overhead ) * 100

    return {
        "num_switches": num_switches,
        "cpu_utilization": round(cpu_utilization, 4)
    }

  def main(self):
    pending = sorted(self.processes, key=lambda x: x.gz)
    ready_queue = deque()


    while pending or ready_queue:
        while pending and pending[0].gz <= self.simdi:
            ready_queue.append(pending.pop(0))

        if not ready_queue:
            idle_start = self.simdi
            self.simdi = pending[0].gz
            self.context_stats.append({
                'ID': 'IDLE',
                'Baslangic': idle_start,
                'Bitis': self.simdi,
                'Gelis': idle_start,
                'Islem_Suresi': self.simdi - idle_start
            })
            continue

        p = ready_queue.popleft()
        baslama = self.simdi
        isleme_suresi = min(p.iz, self.quantum)

        self.simdi += isleme_suresi
        p.iz -= isleme_suresi

        self.context_stats.append({
            'ID': p.ID,
            'Baslangic': baslama,
            'Bitis': self.simdi,
            'Gelis': p.gz, # We keep original arrival to calculate TAT later
            'Islem_Suresi': isleme_suresi
        })

        while pending and pending[0].gz <= self.simdi:
            ready_queue.append(pending.pop(0))

        if p.iz > 0:
            ready_queue.append(p)
        else:
            p.state = "finished"

        print(f"[ {baslama} ] - - {p.ID} - - [ {self.simdi} ]")

#A = RR("testtest.txt", 2)
#A.main()
#A.export_timeline()
#print(A.calculate_cpu_utilization() )
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

class PJF_Preemptive():
  def __init__(self, path):
    self.simdi = 0
    self.raporu_stats = []
    self.processes = self.read_csv(path)
    #self.quantum = quantum
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

  from pathlib import Path

  def export_timeline(self):
    output_path = f"{Path(self.path).stem}_PJF_Preemptive.txt"
    print(output_path)
    try:
        with open(output_path, 'w') as file:
            current_clock = 0

            for segment in self.context_stats:
                start = segment['Baslangic']
                end = segment['Bitis']

                if start > current_clock:
                    idle_line = f"[ {current_clock} ] - - IDLE - - [ {start} ]\n"
                    file.write(idle_line)

                process_line = f"[ {start} ] - - {segment['ID']} - - [ {end} ]\n"
                file.write(process_line)

                current_clock = end

        print(f"Timeline with IDLE gaps successfully exported to {output_path}")

    except Exception as e:
        print(f"Error exporting timeline: {e}")

  def bekleme_stats(self):
    process_data = {}
    for segment in self.context_stats:
        pid = segment['ID']
        if pid == 'IDLE': continue
        work_done = segment['Bitis'] - segment['Baslangic']

        if pid not in process_data:
            process_data[pid] = {
                'Gelis': segment['Gelis'],
                'Bitis': segment['Bitis'],
                'Toplam_Islem': work_done
            }
        else:
            process_data[pid]['Bitis'] = segment['Bitis']
            process_data[pid]['Toplam_Islem'] += work_done

    waiting_times = [ (d['Bitis'] - d['Gelis']) - d['Toplam_Islem'] for d in process_data.values() ]

    return {
        "ortalama": round(sum(waiting_times) / len(waiting_times), 2) if waiting_times else 0,
        "maksimum": max(waiting_times) if waiting_times else 0
    }

  def turnaround_stats(self):
    process_data = {}

    for segment in self.context_stats:
        pid = segment['ID']
        if pid == 'IDLE':
            continue

        if pid not in process_data:
            process_data[pid] = {
                'Gelis': segment['Gelis'], # Sisteme ilk giriş zamanı
                'Bitis': segment['Bitis']  # Gördüğümüz son bitiş zamanı
            }
        else:
            process_data[pid]['Bitis'] = segment['Bitis']

    turnaround_times = []
    for pid, data in process_data.items():
        turnaround = data['Bitis'] - data['Gelis']
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
        pid = segment['ID']
        if pid != 'IDLE':
            completion_times[pid] = segment['Bitis']

    final_times = list(completion_times.values())
    throughput_results = {}

    for limit in time_limits:
        count = sum(1 for finish_time in final_times if finish_time <= limit)
        throughput_results[f"T={limit}"] = count

    return throughput_results

  def calculate_cpu_utilization(self, context_switch_time=0.01):
    if not self.context_stats:
        return {"cpu_utilization": 0}

    total_cpu_burst_time = sum(
        (s['Bitis'] - s['Baslangic']) for s in self.context_stats
    )

    num_switches = 0
    for i in range(len(self.context_stats) - 1):
        current_segment = self.context_stats[i]
        next_segment = self.context_stats[i+1]

        if current_segment['ID'] != next_segment['ID']:
            num_switches += 1


        elif next_segment['Baslangic'] > current_segment['Bitis']:
            num_switches += 1

    total_overhead = num_switches * context_switch_time
    total_elapsed_time = self.context_stats[-1]['Bitis']
    total_time_with_overhead = total_elapsed_time + total_overhead
    cpu_utilization = (total_cpu_burst_time / total_time_with_overhead) * 100 

    return {
        "num_switches": num_switches,
        "cpu_utilization": round(cpu_utilization, 4)
    }

  def main(self):
    current_p = None
    current_p_gz = None # 
    start = self.simdi

    while (len ([p for p in self.processes if p.state != 'finished']) != 0):
      ### print(f"\n\n--------------------------------simdi {self.simdi}-------------")

      ram = [p for p in self.processes if ( p.gz <= self.simdi and p.state != 'finished')]

      # Handle IDLE state
      if len(ram) == 0:
        if current_p is not None:

          self.context_stats.append({'ID': current_p, 'Baslangic': start, 'Bitis': self.simdi, 'Gelis': current_p_gz})
          current_p = None
        if not self.context_stats or self.context_stats[-1]['ID'] != 'IDLE':
            self.context_stats.append({'ID': 'IDLE', 'Baslangic': self.simdi, 'Bitis': self.simdi + 1, 'Gelis': self.simdi})
        else:
            self.context_stats[-1]['Bitis'] += 1

        self.simdi += 1
        start = self.simdi
        continue

      for p in self.processes:
        if p in ram:
          p.state = "ready"
      prio_map = {'high': 1, 'normal': 2, 'low': 3}
      ram = sorted(ram, key=lambda x: (prio_map[x.priority], x.gz))
      p = ram[0]

      if p.ID != current_p:
        if current_p is not None:

          self.context_stats.append({'ID': current_p, 'Baslangic': start, 'Bitis': self.simdi, 'Gelis': current_p_gz})

        current_p = p.ID
        current_p_gz = p.gz # Store the arrival time of the new process
        start = self.simdi

      self.simdi += 1
      p.iz -= 1

      if p.iz == 0:
        p.state = "finished"
        self.raporu_stats.append({'ID': p.ID, 'Bitis': self.simdi, 'Gelis': p.gz})

    if current_p is not None:
        self.context_stats.append({'ID': current_p, 'Baslangic': start, 'Bitis': self.simdi, 'Gelis': current_p_gz})

    zaman_tablosu_line = f"[ {start} ]-- {current_p} -- [ {self.simdi} ]"

#A = PJF_Preemptive("testtest.txt")
#A.main()
#A.export_timeline()
#print(A.calculate_cpu_utilization() )
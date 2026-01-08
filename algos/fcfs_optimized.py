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


from pathlib  import Path
class FCFS():
  def __init__(self, path):
    self.simdi = 0
    self.processes = []
    self.raporu_stats = []
    self.baglam_degistirme_stats = []
    self.processes = self.read_csv(path)
    self.ram = []
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
    output_path = f"{Path(self.path).stem}_FCFS.txt"

    try:
        with open(output_path, 'w') as file:
            last_end_time = 0

            for segment in self.raporu_stats:
                current_start = segment['Baslangic']
                current_end = segment['Bitis']

                if current_start > last_end_time:
                    idle_line = f"[ {last_end_time} ] - - IDLE - - [ {current_start} ]\n"
                    file.write(idle_line)

                line = f"[ {current_start} ] - - {segment['ID']} - - [ {current_end} ]\n"
                file.write(line)

                last_end_time = current_end

        print(f"Zamanlama raporu cikti : {output_path}")

    except Exception as e:
        print(f"hata olmus: {e}")

  def bekleme_stats(self):

    surecler = [s for s in self.raporu_stats if s['ID'] != 'IDLE']
    waiting_times = [s['Bekleme'] for s in surecler]

    return {
        "ortalama": round(sum(waiting_times) / len(waiting_times) , 2),
        "maksimum": round(float(max(waiting_times) ), 2),
    }

  def turnaound_stats(self):

    surecler = [s for s in self.raporu_stats if s['ID'] != 'IDLE']
    waiting_times = [s['Turnaround'] for s in surecler]

    return {
        "ortalama": round(sum(waiting_times) / len(waiting_times) , 2),
        "maksimum": round(float(max(waiting_times) ), 2)
    }

  def throughput_stats(self, time_points=[50, 100, 150, 200]):
    completion_times = [p['Bitis'] for p in self.raporu_stats if p['ID'] != 'IDLE']
    throughput_results = {}

    for t in time_points:
        count = sum(1 for comp_time in completion_times if comp_time <= t)
        throughput_results[f"T={t}"] = count
    return throughput_results

  def calculate_cpu_utilization(self, context_switch_time=0.01):

    real_processes = [p for p in self.raporu_stats if p['ID'] != 'IDLE']
    total_cpu_burst_time = sum(p['Bitis'] - p['Baslangic'] for p in real_processes)

    num_switches = 0
    for i in range(len(self.raporu_stats) - 1):
        if self.raporu_stats[i]['ID'] != self.raporu_stats[i+1]['ID']:
            num_switches += 1
    total_overhead = num_switches * context_switch_time
    total_time_with_overhead = total_cpu_burst_time + total_overhead
    cpu_utilization = (total_cpu_burst_time / total_time_with_overhead ) * 100

    return {
        "num_switches": num_switches,
        "cpu_utilization": round(cpu_utilization, 4)
    }

  def main(self):
        queue = sorted(self.processes, key=lambda x: x.gz)

        for p in queue:
            if self.simdi < p.gz:
                idle_start = self.simdi
                self.simdi = p.gz
                self.raporu_stats.append({
                    'ID': 'IDLE',
                    'Baslangic': idle_start,
                    'Bitis': self.simdi,
                    'Bekleme': 0
                })

            start_time = self.simdi
            waiting_time = start_time - p.gz
            finish_time = start_time + p.iz

            self.simdi = finish_time
            p.state = "finished"

            self.raporu_stats.append({
                'ID': p.ID,
                'Baslangic': start_time,
                'Bitis': finish_time,
                'Gelis_Zamani': p.gz,
                'Bekleme': waiting_time,
                'Turnaround': finish_time - p.gz
            })

            print(f"[ {start_time} ]-- {p.ID} -- [ {finish_time} ]")

#A = FCFS("testtest.txt")
#A.main()
#A.export_timeline()
#print(A.calculate_cpu_utilization() )
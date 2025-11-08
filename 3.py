def findWaitingTime(processes, n, bt, wt):
    sorted_processes = sorted([(bt[i], processes[i], i) for i in range(n)])
    wt[sorted_processes[0][2]] = 0
    current_time = sorted_processes[0][0]

    for i in range(1, n):
        original_index = sorted_processes[i][2]
        current_bt = sorted_processes[i][0]
        wt[original_index] = current_time
        current_time += current_bt

def findTurnAroundTime(processes, n, bt, wt, tat):
    for i in range(n):
        tat[i] = bt[i] + wt[i]

def findavgTime(processes, n, bt):
    wt = [0] * n
    tat = [0] * n
    total_wt = 0
    total_tat = 0

    findWaitingTime(processes, n, bt, wt)
    findTurnAroundTime(processes, n, bt, wt, tat)

    print("Processes Burst Time Waiting Time Turn Around Time")
    
    results = sorted([(processes[i], bt[i], wt[i], tat[i]) for i in range(n)])

    for p_id, p_bt, p_wt, p_tat in results:
        total_wt += p_wt
        total_tat += p_tat
        print(f" {p_id}\t\t{p_bt}\t\t{p_wt}\t\t{p_tat}")

    print(f"\nAverage waiting time = {total_wt / n}")
    print(f"Average turn around time = {total_tat / n}")

if __name__ == "__main__":
    processes = [1, 2, 3]
    n = len(processes)
    burst_time = [10, 5, 8]
    
    print("--- SJF Scheduling Results ---")
    findavgTime(processes, n, burst_time)

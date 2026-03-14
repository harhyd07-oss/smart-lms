# os_concepts/scheduling.py
# Simulates CPU scheduling algorithms.
#
# OS Concept: The CPU scheduler decides which process runs next.
# Two classic algorithms:
# 1. FCFS — First Come First Served (simplest, no preemption)
# 2. Round Robin — Each process gets a fixed time slice (quantum)

def fcfs_scheduling(requests):
    """
    First Come First Served Scheduling.

    Processes are handled in the order they arrive.
    No preemption — once started, runs to completion.

    Args:
        requests: list of dicts with 'id', 'name', 'burst_time'
    
    Returns:
        List of dicts with scheduling results including
        waiting_time and turnaround_time for each process
    """
    results      = []
    current_time = 0

    for req in requests:
        arrival_time    = req.get('arrival_time', 0)
        burst_time      = req['burst_time']

        # If CPU is free before process arrives, jump to arrival
        if current_time < arrival_time:
            current_time = arrival_time

        waiting_time     = current_time - arrival_time
        start_time       = current_time
        current_time    += burst_time
        finish_time      = current_time
        turnaround_time  = finish_time - arrival_time

        results.append({
            'id':              req['id'],
            'name':            req['name'],
            'burst_time':      burst_time,
            'arrival_time':    arrival_time,
            'waiting_time':    waiting_time,
            'turnaround_time': turnaround_time,
            'start_time':      start_time,
            'finish_time':     finish_time
        })

    return results


def round_robin_scheduling(requests, quantum=3):
    """
    Round Robin Scheduling.

    Each process gets a fixed time quantum.
    If not finished, goes back to the end of the queue.
    This prevents any single process from hogging the CPU.

    Args:
        requests: list of dicts with 'id', 'name', 'burst_time'
        quantum:  time slice each process gets (default 3)
    
    Returns:
        List of scheduling results with waiting and turnaround times
    """
    import copy

    # Work with copies so we don't modify originals
    processes    = copy.deepcopy(requests)
    n            = len(processes)
    current_time = 0
    completed    = 0

    # Track remaining burst time for each process
    remaining    = {p['id']: p['burst_time'] for p in processes}
    finish_time  = {p['id']: 0              for p in processes}
    waiting_time = {p['id']: 0              for p in processes}
    started      = {p['id']: False          for p in processes}
    first_start  = {p['id']: 0              for p in processes}

    queue = list(range(n))  # index queue

    while completed < n:
        made_progress = False

        for i in queue:
            p = processes[i]
            pid = p['id']

            if remaining[pid] <= 0:
                continue

            made_progress = True

            if not started[pid]:
                first_start[pid] = current_time
                started[pid]     = True

            # Run for quantum or remaining time, whichever is smaller
            run_time      = min(quantum, remaining[pid])
            current_time += run_time
            remaining[pid] -= run_time

            if remaining[pid] == 0:
                finish_time[pid] = current_time
                completed       += 1

        if not made_progress:
            break

    results = []
    for p in processes:
        pid             = p['id']
        arrival         = p.get('arrival_time', 0)
        turnaround      = finish_time[pid] - arrival
        wait            = turnaround - p['burst_time']

        results.append({
            'id':              pid,
            'name':            p['name'],
            'burst_time':      p['burst_time'],
            'arrival_time':    arrival,
            'waiting_time':    max(0, wait),
            'turnaround_time': max(0, turnaround),
            'finish_time':     finish_time[pid]
        })

    return results


def calculate_averages(results):
    """
    Calculates average waiting and turnaround times.
    Used to compare FCFS vs Round Robin performance.
    """
    if not results:
        return {'avg_waiting': 0, 'avg_turnaround': 0}

    n = len(results)
    avg_waiting     = sum(r['waiting_time']    for r in results) / n
    avg_turnaround  = sum(r['turnaround_time'] for r in results) / n

    return {
        'avg_waiting':    round(avg_waiting,    2),
        'avg_turnaround': round(avg_turnaround, 2)
    }
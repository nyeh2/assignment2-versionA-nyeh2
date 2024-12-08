#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Nelson Yeh"
Semester: "Fall 2024"

The python code in this file is original work written by
"Nelson Yeh". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: <Enter your documentation here>

'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    # check the docs for an argparse option to store this as a boolean.
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    parser.add_argument('-H', '--human-readable', action='store_true', help='Display memory values in human-readable format (e.g., MiB, GiB).')
    args = parser.parse_args()
    return args


def percent_to_graph(percent: float, length: int=20) -> str:
    "turns a percent 0.0 - 1.0 into a bar graph"
    try:
        # Ensure percent is within valid range
        if (0.0<= percent <= 1.0):
            # Calculate the number of filled bars
            fill = int(percent * length)
            # Create the bar graph string
            return('#' * fill + ' '* (length-fill))
    except ValueError:
        # Handle invalid input
        return("Percent must be between 0.0 and 1.0")

    ...
# percent to graph function

def get_sys_mem() -> int:
    "return total system memory (used or available) in kB"
    # Open the system memory info file
    mem_info = open('/proc/meminfo', 'r')
    for line in mem_info:
        # Look for the line containing total memory
        if 'MemTotal' in line:
            # Extract memory value
            sys_mem = int(line.split()[1])
            return sys_mem
    # Close the file after reading
    mem_info.close()

    ...

def get_avail_mem() -> int:
    "return total memory that is available"
    # Open the system memory info file
    mem_info = open('/proc/meminfo', 'r')
    for line in mem_info:
        # Look for the line containing available memory
        if 'MemAvailable' in line:
            # Extract memory value
            avail_mem = int(line.split()[1])
            return avail_mem
    # Close the file after reading
    mem_info.close()
    ...

def pids_of_prog(app_name: str) -> list:
    "given an app name, return all pids associated with app"
    # Get process IDs
    pids = os.popen('pidof ' + app_name).read().strip()
    if pids:
        # Split the result into a list of PIDs
        pids_list = pids.split()
    else:
        # Return an empty list if no PIDs are found
        pids_list = []
    return pids_list
    ...

def rss_mem_of_pid(proc_id: str) -> int:
    "given a process id, return the resident memory used, zero if not found"
    try:
        # Open the smaps file for the process
        smaps = open(f'/proc/{proc_id}/smaps')
        for line in smaps:
            # Look for the line containing RSS memory
            if 'VmRSS' in line:
                # Extract the memory value
                total_rss = int(line.split()[1])
                return total_rss
    except (FileNotFoundError):
        # Handle cases where the process doesnt exists
        return 0
    return 0
    ...

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_command_args()

    # Get total and available memory
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    if not args.program:
        # Calculate used memory
        used_mem = total_mem - avail_mem
        # Calculate memory used in decimal
        percent_used_dec = used_mem/total_mem
        # Calculate memory used in percentage
        percent_used = (used_mem/total_mem)*100
        # Generate bar graph
        bar = percent_to_graph(percent_used_dec, args.length)

        if args.human_readable:
             # Convert values to human-readable format
            used_mem_read = bytes_to_human_r(used_mem)
            total_mem_read = bytes_to_human_r(total_mem)
            print(f'Memory:  [{bar}|{percent_used:.0f}%]  {used_mem_read}/{total_mem_read}')
        else:
            # Print memory usage in raw format
            print(f'Memory:  {bar}|{percent_used:.0f}%]  {used_mem}/{total_mem}')

    else:
        # Program specified. Show memory usage for all associated processes
        pids = pids_of_prog(args.program)
        if not pids:
            # Print error if program not found
            print(f'{args.program} not found')
        else:
            # Initialize total memory used by the program
            total_program_rss = 0
            for pid in pids:
                # Get memory usage for each PID
                pid_rss = rss_mem_of_pid(pid)
                # Accumulate memory usage
                total_program_rss += pid_rss
                # Calculate percentage of memory used
                percent_used_dec = pid_rss / total_mem
                # Generate bar graph
                bar = percent_to_graph(percent_used_dec, args.length)

                if args.human_readable:
                    # Convert values to human-readable format
                    pid_rss_str = bytes_to_human_r(pid_rss)
                    total_mem_str = bytes_to_human_r(total_mem)
                    print(f"{pid}  [{bar}|{percent_used_dec*100:.0f}%] {pid_rss_str}/{total_mem_str}")
                else:
                    # Print memory usage in raw format
                    print(f"{pid}  [{bar}|{percent_used_dec*100:.0f}%] {pid_rss}/{total_mem}")

             # Calculate total memory usage for the program
            percent_used_dec = total_program_rss / total_mem
            bar = percent_to_graph(percent_used_dec, args.length)

            if args.human_readable:
                # Convert values to human-readable format
                total_rss_str = bytes_to_human_r(total_program_rss)
                total_mem_str = bytes_to_human_r(total_mem)
                print(f"{args.program}  [{bar}|{percent_used_dec*100:.0f}%] {total_rss_str}/{total_mem_str}")
            else:
                # Print memory usage in raw format
                print(f"{args.program}  [{bar}|{percent_used_dec*100:.0f}%] {total_program_rss}/{total_mem}")
        ...
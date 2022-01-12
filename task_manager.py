#########################################
#    Advanced Operating System project  #
#    Project : Build Task Manager       #
#    Name: Moksh Shah                   #
#########################################

import os
import pwd, heapq
import warnings

warnings.filterwarnings("ignore")
import tkinter
from tkinter import *
from tkinter import ttk

global buffer_time
buffer_time = 2 * 1000

prev_utilization_time = 0
prev_system_time = 0
previous_idle = 0
prev_context = 0
prev_interrupts = 0
previous_free_memory = 0
prev_read_data = 0
prev_write_data = 0
prev_disk_read_data = 0
prev_disk_write_data = 0
previous_data_trans = 0
top_process_list = 20
prev_cpu_process = 0


class Task_Manager_OS:
    # CPU UTILIZATION CODE
    """
    CPU utilization in percentage: user mode, sys mode, overall utilization
    The number of interrupts
    The number of context switches
    """

    def cpu_utilization(self):

        global prev_utilization_time
        global prev_system_time
        global previous_idle
        global prev_context
        global prev_interrupts

        total_number_cpu = 0
        # Get CPU utilization data in percentage
        with open("/proc/stat", "r") as f:
            file = f.readlines()

            for line in file:
                columns = line.split()

                if "cpu" in columns[0]:
                    total_number_cpu += 1

                if "cpu" == columns[0]:
                    current_utilization_time = float(columns[1])
                    current_system_time = float(columns[3])
                    current_idle = float(columns[4])

                    util_user_time = current_utilization_time - prev_utilization_time
                    util_sys_time = current_system_time - prev_system_time
                    idle_time = current_idle - previous_idle
                    total_time_cpu = util_user_time + util_sys_time + idle_time
                    util_cpu_time = util_user_time + util_sys_time + current_idle - previous_idle

                    total_utilization = ((util_user_time + util_sys_time) / util_cpu_time) * 100
                    system_utilization = (
                            ((float(util_user_time) + float(util_sys_time)) / float(total_time_cpu)) * 100.00)
                    system_mode = ((float(util_sys_time) / float(total_time_cpu)) * 100.00)
                    user_mode = ((float(util_user_time) / float(total_time_cpu)) * 100.00)

                    previous_idle = current_idle
                    prev_utilization_time = current_utilization_time
                    prev_system_time = current_system_time

                # Get number of interrupts
                elif "intr" == columns[0]:
                    current_interrupts = int(columns[1])
                    total_interrupts = current_interrupts - prev_interrupts
                    prev_interrupts = current_interrupts

                # Get number of context switches
                elif "ctxt" == columns[0]:
                    current_context = int(columns[1])
                    total_context = (current_context - prev_context)
                    prev_context = current_context

        # Storing all cpu related information in a list
        self.cpu_utilization_info = [str(total_number_cpu - 1), str(round(total_utilization, 2)),
                                     str(total_interrupts / buffer_time), str(total_context / buffer_time),
                                     str(system_utilization), str(round(system_mode, 2)), str(round(user_mode, 2))]

    # MEMORY UTILIZATION CODE
    """
    The memory utilization: available memory (MB), total memory (MB), memory utilization (percentage)
    """

    def memory_utilization(self):
        global previous_free_memory
        total_memory = 0

        # Get memory information to collect avail memory, total memory and memory utilization
        with open("/proc/meminfo", "r") as f:
            file = f.readlines()
            index = 0
            for mem in file:
                col_list = mem.split()

                if index == 0:
                    total_memory = float(col_list[1]) / (1024 * 1024)
                if index == 1:
                    current_free_memory = float(col_list[1])
                    break
                index += 1

        available_memory = (current_free_memory - previous_free_memory) / (1024 * 1024)
        average_free_memory = ((previous_free_memory + current_free_memory) / 2) / (1024 * 1024)
        memory_utilization = ((total_memory - average_free_memory) / total_memory) * 100
        previous_free_memory = current_free_memory

        self.memory_information = [str(round(total_memory, 2)), str(round(average_free_memory, 2)),
                                   str(round(memory_utilization, 2)), str(round(available_memory, 2))]

    # DISK STAT UTILIZATION CODE
    """
    Write a Function to get all the information listed below:-
    The number of disk reads
    The number of blocks read
    The number of disk writes
    The number of blocks written
    """

    def disk_stat_util(self):

        global prev_read_data
        global prev_write_data
        global prev_disk_read_data
        global prev_disk_write_data

        with open("/proc/diskstats", "r") as f:
            file = f.readlines()

            for line in file:
                col_list = line.split()
                if col_list[2] == "sda":
                    current_read = float(col_list[5])
                    current_write = float(col_list[9])
                    current_disk_read = float(col_list[3])
                    current_disk_write = float(col_list[7])

                    disk_read = ((current_disk_read - prev_disk_read_data) / buffer_time)
                    disk_write = ((current_disk_write - prev_disk_write_data) / buffer_time)
                    block_read = ((current_read - prev_read_data) / buffer_time)
                    block_write = ((current_write - prev_write_data) / buffer_time)
                    disk_util = (((current_read + current_write - prev_read_data - prev_write_data) / buffer_time)
                                 * 512) / (10 ** 6)

                    prev_write_data, prev_read_data = current_write, current_read
                    prev_disk_write_data, prev_disk_read_data = current_disk_write, current_disk_read

        self.disk_information = [str(round(disk_util, 2)), str(disk_read), str(disk_write), str(block_read),
                                 str(block_write)]

    # NETWORK UTILIZATION CODE
    """
    Function to get network utilization information
    The number of established and active TCP connections
    """

    def network_utilization_info(self):
        global previous_data_trans

        with open("/proc/net/dev") as f:
            count = 0  # to neglet scanning first line
            network_device = []

            for lines in f.readlines():
                if count > 1:
                    network_data = lines.split()
                    if "lo" in network_data[0]:
                        pass
                    else:
                        network_device.append(network_data[0].split(":")[0])
                        current_data_trans = float(network_data[1]) + float(
                            network_data[9])  # received and transmitted bytes
                else:
                    count += 1

        network_util_proc = float(((current_data_trans - previous_data_trans) / 2)) / 1024
        previous_data_trans = current_data_trans

        with open("/proc/net/tcp", "r") as f:
            number_of_connections = 0
            total_number_of_connections = 0
            for line in f:
                col_list = line.split()
                if col_list[3] == "01":
                    number_of_connections += 1
                else:
                    total_number_of_connections += 1

        self.network_information = [str(round(network_util_proc, 2)), str(number_of_connections),
                                    str(total_number_of_connections + number_of_connections)]  # speed of network

    # NETWORK TCP/UDP CODE
    """
    Write a function to get all the information TCP/UDP connections with username, program, 
    source and destination addresses
    """

    def get_net_tcp_udp(self):
        def compare_inode(inode, local_address, loc_socket, remote_address, remote_socket, c_type, uid, l1):
            for file in os.listdir("/proc"):
                if file.isdigit():
                    try:
                        path = "/proc/" + str(file) + "/fd"

                        for fd_files in os.listdir(path):
                            socket = os.stat(path + "/" + fd_files).st_ino
                            if socket == inode:
                                with open("/proc/" + str(file) + "/comm") as file_pname:
                                    p_name = file_pname.readlines()[0].split("\n")[0]

                                user_name = pwd.getpwuid(uid).pw_name
                                loc_list = [c_type, local_address, loc_socket, remote_address, loc_socket,
                                            remote_address, remote_socket, user_name, p_name]
                                l1.append(loc_list)
                            # print(self.connection_info)
                    except Exception as e:
                        pass

        def convert_to_ip(s):

            bytes_b = ["".join(x) for x in zip(*[iter(s)] * 2)]
            bytes_b = [int(x, 16) for x in bytes_b]
            return ".".join(str(x) for x in reversed(bytes_b))

        def port(s):
            return str(int(s, 16))

        self.connection_info = list()
        with open("/proc/net/tcp", "r") as f:
            start_read = False
            for line in f.readlines():
                if start_read == False:
                    start_read = True
                else:
                    field = line.split()
                    # print(field)
                    local_address = convert_to_ip(field[1].split(":")[0])
                    remote_address = convert_to_ip(field[2].split(":")[0])
                    loc_socket = port(field[1].split(":")[1])
                    remote_socket = port(field[2].split(":")[1])
                    inode = int(field[9])
                    uid = int(field[7])
                    # print(inode, uid)
                    compare_inode(inode, local_address, loc_socket, remote_address, remote_socket, "tcp", uid,
                                  self.connection_info)

    # PROCESS UTILIZATION CODE
    """
    Process CPU utilization in percentage: user mode, sys mode, overall utilization
    Process virtual memory utilization
    Process physical memory utilization
    User name and program name
    """

    def process_utilization(self):
        global top_process_list
        global prev_cpu_process

        with open('/proc/stat') as f:
            data_cpu = f.readlines()
            for line in data_cpu:
                total_memory = float(line.strip().split()[1:2][0])
                break

        def get_names(pid):
            # print("--------------------in get_name-------------" , pid)
            try:
                with open("/proc/" + str(pid) + "/comm", "r") as file_pname:
                    pname = file_pname.readlines()[0].split("\n")[0]
                    # print(pname)
                with open("/proc/" + str(pid) + "/status", "r") as file_uid:
                    data = file_uid.readlines()
                    for line in data:
                        columns = line.split("\t")
                        if columns[0] == "Uid:":
                            uid = columns[1]
                            uname = pwd.getpwuid(int(uid)).pw_name
                            break

                return uname, pname

            except Exception as e:
                pass

        def get_vmsize(path):
            path = path + "/status"
            with open(path, "r") as file:
                data = file.readlines()
                vm_size = float(data[17].split(":")[1].split()[0]) * 1000 * 8
                return vm_size

        def heappush(h, item, key=lambda x: x[3]):
            heapq.heappush(h, (key(item), item))

        # def heappop(h):
        #     heapq.heappop(h)[1]

        for_one_pass = True
        need_vm = True
        per_process_info = list()
        heapq.heapify(per_process_info)

        with open('/proc/stat', "r") as f:
            data_cpu = f.readlines()
            field = list()
            for line in data_cpu:
                field = line.split()[1:]
                break
            total_number_cpu = float(field[0]) + float(field[2]) + float(field[3])
            if not for_one_pass:
                diff = total_number_cpu - prev_cpu_process
            prev_cpu_process = total_number_cpu
            # print("-------end of CPU task-------------------")

        for p_id in os.listdir("/proc"):
            if p_id.isdigit():
                try:
                    path_stat = "/proc/" + str(p_id) + "/stat"

                    if need_vm == True:
                        vmsize = get_vmsize("/proc/" + str(p_id))
                        need_vm = False

                    with open(path_stat) as f:
                        data = f.readlines()[0].split()
                        p_cpu = float(data[13]) + float(data[14])  # jiffy
                        p_vm = float(data[22]) / (8 * 1024 * 1024)  # bytes
                        p_mem = (float(data[23]) * 2048) / (8 * 1024 * 1024)  # converting pages to bytes

                        p_uname, p_pname = get_names(p_id)
                        if not p_uname:
                            break

                        p_cpu_util = (p_cpu / total_number_cpu) * 100  # percentage
                        l = [str(p_id), str(p_uname), str(p_pname), str(round(p_cpu_util, 2)), str(round(p_mem, 2)),
                             str(round(p_vm, 2))]

                        heappush(per_process_info, l)

                except Exception as e:
                    print(e)

        self.processes_list = heapq.nlargest(top_process_list, per_process_info)


# GUI IMPLEMENTATION

tk_task_manager = Task_Manager_OS()

r = tkinter.Tk()
r.title("Task Manager")
r.geometry("1500x1000")
note = ttk.Notebook(r)
note.grid(row=1, column=0, rowspan=100, columnspan=300)

frame1 = ttk.Frame(note)
frame2 = ttk.Frame(note)
frame3 = ttk.Frame(note)
frame4 = ttk.Frame(note)

note.add(frame1, text="__CPU__")
note.add(frame2, text="__Disk__")
note.add(frame3, text="_TCP Connection_")
note.add(frame4, text="_Processes_")

tb1 = Text(frame1)
tb1.grid(row=1, column=0, rowspan=100, columnspan=300)

tb2 = Text(frame2)
tb2.grid(row=1, column=0, rowspan=100, columnspan=300)

tb3 = Text(frame3)
tb3.grid(row=1, column=0, rowspan=100, columnspan=300)

tb4 = Text(frame4)
tb4.grid(row=1, column=0, rowspan=100, columnspan=300)


def display_cpu_mem_net():
    tk_task_manager.cpu_utilization()
    tk_task_manager.memory_utilization()
    tk_task_manager.network_utilization_info()

    tb1.delete('1.0', END)
    tb1.insert(END, "# of CPUs\t\t" + "CPU usage (%)\t\t" + "System usage (%)\t\t" + "User usage (%)\t\t" + "\n")
    tb1.insert(END, "  " + tk_task_manager.cpu_utilization_info[0] + '\t\t' + tk_task_manager.cpu_utilization_info[1] +
               '\t\t' + tk_task_manager.cpu_utilization_info[5] + '   \t\t' + tk_task_manager.cpu_utilization_info[
                   6] + '\n\n')
    tb1.insert(END, "Number of Interrupts\t\t")
    tb1.insert(END, tk_task_manager.cpu_utilization_info[2] + '\n\n')
    tb1.insert(END, "Number of Context switches\t\t")
    tb1.insert(END, tk_task_manager.cpu_utilization_info[3] + '\t' + '\n\n')
    tb1.insert(END, "Total_Memory(GB)\t\t\t" + "Avail_Mem(GB)\t\t" + "Mem_Util %\t\t" + "\n")
    tb1.insert(END, tk_task_manager.memory_information[0] + "\t\t\t" + tk_task_manager.memory_information[1] + "\t\t" +
               tk_task_manager.memory_information[2] + '\n\n')
    tb1.insert(END, "Network_Util (KB/s)\t\t")
    tb1.insert(END, tk_task_manager.network_information[0] + '\n')
    tk_task_manager.network_information = list()
    tk_task_manager.cpu_utilization_info = list()
    tk_task_manager.memory_information = list()
    r.after(buffer_time, display_cpu_mem_net)


def display_disk_util():
    tk_task_manager.disk_stat_util()
    tb2.delete('1.0', END)
    tb2.insert(END, "Disk Utilization (%)" + '\n')
    tb2.insert(END, tk_task_manager.disk_information[0] + '\n\n')
    tb2.insert(END, "Disk Reads\t\t" + "Disk Writes" + '\n')
    tb2.insert(END, tk_task_manager.disk_information[1] + "\t\t" + tk_task_manager.disk_information[2] + '\n\n')
    tb2.insert(END, "Block Reads" + "\t\t" + "Block Writes" + '\n')
    tb2.insert(END, tk_task_manager.disk_information[3] + "\t\t" + tk_task_manager.disk_information[4] + '\n\n')
    tk_task_manager.disk_information = list()
    r.after(buffer_time, display_disk_util)


def display_tcp():
    tk_task_manager.get_net_tcp_udp()
    tk_task_manager.network_utilization_info()
    tb3.delete('1.0', END)
    tb3.insert(END, "Total Number of Connections\t\t")
    tb3.insert(END, tk_task_manager.network_information[2] + '\n\n')
    tb3.insert(END, "Number of Active TCP Connections\t\t")
    tb3.insert(END, tk_task_manager.network_information[1] + '\n\n')
    tb3.insert(END, "User_Name\t\t" + "Program\t\t" + "Source Address\t\t\t" + "Remote Address\t\t" + "\n")
    for f in tk_task_manager.connection_info:
        tb3.insert(END, f[7] + '\t\t' + f[8] + '\t\t' + f[1] + ":" + f[2] + '\t\t\t' + f[3] + ":" + f[4] + '\n')
    tk_task_manager.connection_info = list()
    r.after(buffer_time, display_tcp)


def display_processes():
    tk_task_manager.process_utilization()
    tb4.delete('1.0', END)
    tb4.insert(END, "PID\t" + "Name\t\t" + "User\t" + "CPU(%)\t" + "Memory(MB)\t\t" + "Virtual Memory(MB)" + "\n")
    for p in tk_task_manager.processes_list:
        tb4.insert(END, p[1][0] + "\t" + p[1][2] + "\t\t" + p[1][1] + "\t" + p[1][3] + "\t" + p[1][4] + "\t\t" + p[1][
            5] + "\n")
    tk_task_manager.processes_list = list()
    r.after(buffer_time, display_processes)


display_cpu_mem_net()
display_disk_util()
display_tcp()
display_processes()
r.mainloop()

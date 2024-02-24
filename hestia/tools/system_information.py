import platform
import psutil
import GPUtil
import humanize
import time
from datetime import datetime
from tabulate import tabulate
from typing import List, Tuple, Any

def print_header(header: str) -> None:
    """
    Print formatted header
    """
    print(f"+{'-' * (len(header) + 2)}+")
    print(f"|  {header}  |")
    print(f"+{'-' * (len(header) + 2)}+")

def print_info(info_name: str, info_value: Any) -> None:
    """
    Print formatted information
    """
    print(f"{info_name}: {info_value}")

def print_section(header: str, info: List[Tuple[str, Any]]) -> None:
    """
    Print a section with a header and multiple information lines
    """
    print_header(header)
    for info_name, info_value in info:
        print_info(info_name, info_value)
    print()
    
    
def get_size(bytes: float, suffix: str = "B") -> str:
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
    return ""
        
def get_cpu_info() -> Tuple[str, str, str]:
    """
    Get CPU information
    """
    cpu_freq = str(psutil.cpu_freq())
    cpu_usage = str(psutil.cpu_percent())
    cpu_cores = str(psutil.cpu_count())
    return cpu_freq, cpu_usage, cpu_cores

def get_memory_info() -> Tuple[str, str, str]:
    """
    Get memory information
    """
    memory = psutil.virtual_memory()
    memory_total = get_size(memory.total)
    memory_available = get_size(memory.available)
    memory_used = get_size(memory.used)
    return memory_total, memory_available, memory_used

def get_disk_info() -> Tuple[str, str, str]:
    """
    Get disk information
    """
    disk = psutil.disk_usage("/")
    disk_total = get_size(disk.total)
    disk_used = get_size(disk.used)
    disk_free = get_size(disk.free)
    return disk_total, disk_used, disk_free

def get_network_info() -> Tuple[str, str]:
    """
    Get network information
    """
    network = psutil.net_io_counters()
    network_bytes_sent = get_size(network.bytes_sent)
    network_bytes_recv = get_size(network.bytes_recv)
    return network_bytes_sent, network_bytes_recv

def get_gpu_info() -> List[Tuple[str, str, str, str, str, str, str, str]]:
    """
    Get GPU information
    """
    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        gpu_id = gpu.id
        gpu_name = gpu.name
        gpu_load = f"{gpu.load*100}%"
        gpu_free_memory = f"{gpu.memoryFree}MB"
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid
        list_gpus.append((
            gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
            gpu_total_memory, gpu_temperature, gpu_uuid
        ))
    return list_gpus

def get_boot_info() -> str:
    """
    Get boot time
    """
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    return f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"

def get_system_info() -> Tuple[str, str, str, str]:
    """
    Get system information
    """
    system = platform.uname()
    system_name = system.system
    system_version = system.version
    system_release = system.release
    system_machine = system.machine
    return system_name, system_version, system_release, system_machine

def get_processes_info() -> List[Tuple[str, str, str, str]]:
    """
    Get process information
    """
    processes = []
    for process in psutil.process_iter():
        pid = process.pid
        process_name = process.name()
        process_status = process.status()
        process_creation_time = datetime.fromtimestamp(process.create_time())
        processes.append((
            pid, process_name, process_status, process_creation_time
        ))
    return processes

def get_users_info() -> List[Tuple[str, str, str]]:
    """
    Get users information
    """
    users = []
    for user in psutil.users():
        username = user.name
        terminal = user.terminal
        host = user.host
        users.append((
            username, terminal, host
        ))
    return users

def get_current_time() -> str:
    """
    Get current time
    """
    current_time = time.strftime("%H:%M:%S")
    return current_time

def get_current_date() -> str:
    """
    Get current date
    """
    current_date = time.strftime("%d/%m/%Y")
    return current_date

def get_current_datetime() -> str:
    """
    Get current datetime
    """
    current_datetime = time.strftime("%d/%m/%Y %H:%M:%S")
    return current_datetime





def get_current_timezone() -> str:
    """
    Get current timezone
    """
    current_timezone = time.tzname[0]
    return current_timezone


def humanize_seconds(seconds: int) -> str:
    """
    Convert seconds to human readable string
    """
    return humanize.precisedelta(seconds)

def get_system_uptime() -> str:
    """
    Get system uptime
    """
    uptime = int(time.time() - psutil.boot_time())
    return humanize_seconds(uptime)


def tabulate_data(data: List[Tuple[str, str, str, str]], headers: List[str], table_format: str = "fancy_grid") -> None:
    """
    Tabulate data
    """
    print(tabulate(data, headers=headers, tablefmt=table_format))
    
def main() -> None:
    """
    Main function
    """
    # System Information
    system_name, system_version, system_release, system_machine = get_system_info()
    print_section("System Information", [
        ("System", system_name),
        ("Version", system_version),
        ("Release", system_release),
        ("Machine", system_machine),
        ("Boot Time", get_boot_info()),
        ("Current Time", get_current_time()),
        ("Current Date", get_current_date()),
        ("Current Datetime", get_current_datetime()),
        ("Current Timezone", get_current_timezone()),
        ("System Uptime", get_system_uptime())
    ])
    
    # CPU Information
    cpu_freq, cpu_usage, cpu_cores = get_cpu_info()
    if isinstance(cpu_freq, str):
        cpu_freq_str = cpu_freq
    else:
        cpu_freq_str = f"{cpu_freq.current:.2f}Mhz"
    print_section("CPU Information", [
        ("CPU Frequency", cpu_freq_str),
        ("CPU Usage", f"{cpu_usage}%"),
        ("CPU Cores", cpu_cores)
    ])
    
    # Memory Information
    memory_total, memory_available, memory_used = get_memory_info()
    print_section("Memory Information", [
        ("Memory Total", memory_total),
        ("Memory Available", memory_available),
        ("Memory Used", memory_used)
    ])
    
    # Disk Information
    disk_total, disk_used, disk_free = get_disk_info()
    print_section("Disk Information", [
        ("Disk Total", disk_total),
        ("Disk Used", disk_used),
        ("Disk Free", disk_free)
    ])
    
    # Network Information
    network_bytes_sent, network_bytes_recv = get_network_info()
    print_section("Network Information", [
        ("Network Bytes Sent", network_bytes_sent),
        ("Network Bytes Received", network_bytes_recv)
    ])
    
    # GPU Information
    gpus = get_gpu_info()
    print_header("GPU Information")
    headers = ("GPU ID", "GPU Name", "GPU Load", "GPU Free Memory", "GPU Used Memory", "GPU Total Memory", "GPU Temperature", "GPU UUID")
    tabulate_data(gpus, list(headers)) # type: ignore
    print()
    
    # Users Information
    users = get_users_info()
    print_header("Users Information")
    headers = ("Username", "Terminal", "Host")
    tabulate_data(users, list(headers)) # type: ignore
    print()
    
    

if __name__ == "__main__":
    main()
    


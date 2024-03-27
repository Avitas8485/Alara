import platform
import psutil
import GPUtil
import humanize
import time
from datetime import datetime
from tabulate import tabulate
from typing import List, Tuple, Any
from base_tool import Tool, ToolKit

class ScaleBytesTool(Tool):
    def __init__(self):
        self.name = "scale_bytes"
        self.description = "Scale bytes to its proper format"
        self.usage = "scale_bytes [bytes] [suffix]"
        self.dependencies = {}
        
    def run(self, bytes: float, suffix: str = "B")-> str:
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f} {unit}{suffix}"
            bytes /= factor
        return ""
    
class HumanizeSecondsTool(Tool):
    def __init__(self):
        self.name = "humanize_seconds"
        self.description = "Convert seconds to human readable string"
        self.usage = "humanize_seconds [seconds]"
        self.dependencies = {}
        
    def run(self, seconds: int)-> str:
        return humanize.precisedelta(seconds)
    
class SystemUptimeTool(Tool):
    def __init__(self):
        self.name = "system_uptime"
        self.description = "Get system uptime"
        self.usage = "system_uptime"
        self.dependencies = {}
        
    def run(self)-> str:
        uptime = int(time.time() - psutil.boot_time())
        return humanize.precisedelta(uptime)
    
class CurrentTimeTool(Tool):
    def __init__(self):
        self.name = "current_time"
        self.description = "Get current time"
        self.usage = "current_time"
        self.dependencies = {}
        
    def run(self)-> str:
        return time.strftime("%H:%M:%S")
    
class CurrentDateTool(Tool):
    def __init__(self):
        self.name = "current_date"
        self.description = "Get current date"
        self.usage = "current_date"
        self.dependencies = {}
        
    def run(self)-> str:
        return time.strftime("%d/%m/%Y")
    
class CurrentDatetimeTool(Tool):
    def __init__(self):
        self.name = "current_datetime"
        self.description = "Get current datetime"
        self.usage = "current_datetime"
        self.dependencies = {}
        
    def run(self)-> str:
        return time.strftime("%d/%m/%Y %H:%M:%S")
    
class CurrentTimezoneTool(Tool):
    def __init__(self):
        self.name = "current_timezone"
        self.description = "Get current timezone"
        self.usage = "current_timezone"
        self.dependencies = {}
        
    def run(self)-> str:
        return time.tzname[0]
    
class BootTimeTool(Tool):
    def __init__(self):
        self.name = "boot_time"
        self.description = "Get boot time"
        self.usage = "boot_time"
        self.dependencies = {}
        
    def run(self)-> str:
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        return f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
    
class CpuInfoTool(Tool):
    def __init__(self):
        self.name = "cpu_info"
        self.description = "Get CPU information"
        self.usage = "cpu_info"
        self.dependencies = {}
        
    def run(self)-> Tuple[str, str, str]:
        cpu_freq = str(psutil.cpu_freq())
        cpu_usage = str(psutil.cpu_percent())
        cpu_cores = str(psutil.cpu_count())
        return cpu_freq, cpu_usage, cpu_cores
    
class MemoryInfoTool(Tool):
    def __init__(self):
        self.name = "memory_info"
        self.description = "Get memory information"
        self.usage = "memory_info"
        self.dependencies = {"scale_bytes": ScaleBytesTool()}
        
    def run(self)-> Tuple[str, str, str]:
        memory = psutil.virtual_memory()
        memory_total = self.dependencies['scale_bytes'].run(memory.total, "B")
        memory_available = self.dependencies['scale_bytes'].run(memory.available, "B")
        memory_used = self.dependencies['scale_bytes'].run(memory.used, "B")
        return memory_total, memory_available, memory_used
    
class DiskInfoTool(Tool):
    def __init__(self):
        self.name = "disk_info"
        self.description = "Get disk information"
        self.usage = "disk_info"
        self.dependencies = {"scale_bytes": ScaleBytesTool()}
        
    def run(self)-> Tuple[str, str, str]:
        disk = psutil.disk_usage("/")
        disk_total = self.dependencies['scale_bytes'].run(disk.total, "B")
        disk_used = self.dependencies['scale_bytes'].run(disk.used, "B")
        disk_free = self.dependencies['scale_bytes'].run(disk.free, "B")
        return disk_total, disk_used, disk_free
    
class NetworkInfoTool(Tool):
    def __init__(self):
        self.name = "network_info"
        self.description = "Get network information"
        self.usage = "network_info"
        self.dependencies = {"scale_bytes": ScaleBytesTool()}
        
    def run(self)-> Tuple[str, str]:
        network = psutil.net_io_counters()
        network_bytes_sent = self.dependencies['scale_bytes'].run(network.bytes_sent, "B")
        network_bytes_recv = self.dependencies['scale_bytes'].run(network.bytes_recv, "B")
        return network_bytes_sent, network_bytes_recv
    
class GpuInfoTool(Tool):
    def __init__(self):
        self.name = "gpu_info"
        self.description = "Get GPU information"
        self.usage = "gpu_info"
        self.dependencies = {}
        
    def run(self)-> List[Tuple[int, str, str, str, str, str, str, str]]:
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
    
class ProcessesInfoTool(Tool):
    def __init__(self):
        self.name = "processes_info"
        self.description = "Get process information"
        self.usage = "processes_info"
        self.dependencies = {}
        
    def run(self)-> List[Tuple[int, str, str, datetime]]:
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
    
class UsersInfoTool(Tool):
    def __init__(self):
        self.name = "users_info"
        self.description = "Get users information"
        self.usage = "users_info"
        self.dependencies = {}
        
    def run(self)-> List[Tuple[str, str, str]]:
        users = []
        for user in psutil.users():
            username = user.name
            terminal = user.terminal
            host = user.host
            users.append((
                username, terminal, host
            ))
        return users
    
class SystemInfoToolkit(ToolKit):
    def __init__(self):
        super().__init__()
        self.add_tool(ScaleBytesTool())
        self.add_tool(BootTimeTool())
        self.add_tool(CurrentTimeTool())
        self.add_tool(CurrentDateTool())
        self.add_tool(CurrentDatetimeTool())
        self.add_tool(CurrentTimezoneTool())
        self.add_tool(SystemUptimeTool())
        self.add_tool(CpuInfoTool())
        self.add_tool(MemoryInfoTool())
        self.add_tool(DiskInfoTool())
        self.add_tool(NetworkInfoTool())
        self.add_tool(GpuInfoTool())
        self.add_tool(ProcessesInfoTool())
        self.add_tool(UsersInfoTool())
        
    def __str__(self)-> str:
        return "\n".join([str(tool) for tool in self.tools.values()])
    
if __name__ == '__main__':
    toolkit = SystemInfoToolkit()
    print(toolkit)
    
    # test the tools
    print(toolkit.run("scale_bytes", 1024, "B"))
    print(toolkit.run("boot_time"))
    print(toolkit.run("current_time"))
    print(toolkit.run("current_date"))
    print(toolkit.run("current_datetime"))
    print(toolkit.run("current_timezone"))
    print(toolkit.run("system_uptime"))
    print(toolkit.run("cpu_info"))
    print(toolkit.run("memory_info"))
    print(toolkit.run("disk_info"))
    print(toolkit.run("network_info"))
    print(toolkit.run("gpu_info"))
    print(toolkit.run("processes_info"))

    
    
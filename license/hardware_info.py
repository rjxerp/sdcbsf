#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硬件信息获取模块
用于获取设备的唯一标识信息，如主板序列号、MAC地址等
"""

import subprocess
import re
import uuid
import platform
import hashlib

class HardwareInfo:
    """硬件信息获取类"""
    
    def __init__(self):
        """初始化硬件信息获取类"""
        self.system = platform.system()
    
    def get_motherboard_serial(self):
        """
        获取主板序列号
        :return: 主板序列号字符串，获取失败返回None
        """
        try:
            if self.system == "Windows":
                # 在Windows上使用wmic命令获取主板序列号
                cmd = "wmic baseboard get serialnumber"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                serial = output.strip().split('\n')[1].strip()
                return serial if serial else None
            elif self.system == "Linux":
                # 在Linux上从/sys/class/dmi/id/board_serial文件获取
                with open('/sys/class/dmi/id/board_serial', 'r') as f:
                    return f.read().strip()
            elif self.system == "Darwin":
                # 在macOS上使用system_profiler命令获取
                cmd = "system_profiler SPHardwareDataType | grep 'Serial Number (system)'"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                serial = output.split(':')[-1].strip()
                return serial
        except Exception as e:
            print(f"获取主板序列号失败: {e}")
            return None
    
    def get_mac_address(self):
        """
        获取MAC地址
        :return: MAC地址字符串，获取失败返回None
        """
        try:
            # 使用uuid模块获取MAC地址
            mac = uuid.getnode()
            mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0, 48, 8)])
            return mac_str
        except Exception as e:
            print(f"获取MAC地址失败: {e}")
            return None
    
    def get_cpu_info(self):
        """
        获取CPU信息
        :return: CPU信息字符串，获取失败返回None
        """
        try:
            if self.system == "Windows":
                cmd = "wmic cpu get name"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                cpu_info = output.strip().split('\n')[1].strip()
                return cpu_info if cpu_info else None
            elif self.system == "Linux":
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            return line.split(':')[-1].strip()
            elif self.system == "Darwin":
                cmd = "sysctl -n machdep.cpu.brand_string"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                return output.strip()
        except Exception as e:
            print(f"获取CPU信息失败: {e}")
            return None
    
    def get_disk_serial(self):
        """
        获取磁盘序列号
        :return: 磁盘序列号字符串，获取失败返回None
        """
        try:
            if self.system == "Windows":
                cmd = "wmic diskdrive get serialnumber"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                serial = output.strip().split('\n')[1].strip()
                return serial if serial else None
            elif self.system == "Linux":
                # 在Linux上获取第一个磁盘的序列号
                cmd = "lsblk -o NAME,SERIAL | grep -E 'sd[a-z]$' | head -1"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                parts = output.strip().split()
                return parts[1] if len(parts) > 1 else None
            elif self.system == "Darwin":
                cmd = "system_profiler SPSerialATADataType | grep 'Serial Number'"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                serial = output.split(':')[-1].strip()
                return serial
        except Exception as e:
            print(f"获取磁盘序列号失败: {e}")
            return None
    
    def get_unique_machine_id(self):
        """
        生成唯一的机器ID，基于多个硬件信息的哈希值
        :return: 唯一机器ID字符串
        """
        # 收集所有可用的硬件信息
        hardware_data = []
        
        motherboard = self.get_motherboard_serial()
        if motherboard:
            hardware_data.append(motherboard)
        
        mac = self.get_mac_address()
        if mac:
            hardware_data.append(mac)
        
        cpu = self.get_cpu_info()
        if cpu:
            hardware_data.append(cpu)
        
        disk = self.get_disk_serial()
        if disk:
            hardware_data.append(disk)
        
        # 如果没有收集到任何硬件信息，使用随机生成的UUID（不推荐，但作为备选）
        if not hardware_data:
            hardware_data.append(str(uuid.uuid4()))
        
        # 生成哈希值作为唯一机器ID
        machine_id_str = '|'.join(hardware_data)
        machine_id = hashlib.sha256(machine_id_str.encode('utf-8')).hexdigest()
        
        return machine_id

if __name__ == "__main__":
    # 测试硬件信息获取
    hardware = HardwareInfo()
    print(f"主板序列号: {hardware.get_motherboard_serial()}")
    print(f"MAC地址: {hardware.get_mac_address()}")
    print(f"CPU信息: {hardware.get_cpu_info()}")
    print(f"磁盘序列号: {hardware.get_disk_serial()}")
    print(f"唯一机器ID: {hardware.get_unique_machine_id()}")
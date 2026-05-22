"""
Advanced System Analysis - تحليل متقدم للنظام
Using multiple programming languages and system tools for deep analysis
"""

import os
import subprocess
import platform
import json
import tempfile
from datetime import datetime


class SystemAnalyzer:
    """Advanced system analysis using multiple tools"""
    
    def __init__(self):
        self.available_tools = self._detect_tools()
    
    def _detect_tools(self):
        """Detect available system tools"""
        tools = {
            'wmic': False,
            'netstat': False,
            'tasklist': False,
            'reg': False,
            'sc': False,
            'certutil': False,
            'signtool': False,
            'powershell': False,
            'vbs': False
        }
        
        if platform.system() == 'Windows':
            # Check Windows tools
            for tool in tools.keys():
                try:
                    if tool == 'powershell':
                        result = subprocess.run(['powershell', '-Command', '$PSVersionTable'], 
                                              capture_output=True, timeout=2)
                    elif tool == 'vbs':
                        result = subprocess.run(['cscript', '//?'], 
                                              capture_output=True, timeout=2)
                    else:
                        result = subprocess.run([tool, '/?'], 
                                              capture_output=True, timeout=2, shell=True)
                    tools[tool] = result.returncode == 0 or result.returncode == 1
                except:
                    pass
        
        return tools
    
    def analyze_file_deep(self, file_path):
        """Deep file analysis using multiple tools"""
        analysis = {
            'file_path': file_path,
            'tools_used': [],
            'results': {}
        }
        
        # WMIC analysis
        if self.available_tools.get('wmic'):
            try:
                # Escape backslashes for WMIC
                escaped_path = file_path.replace('\\', '\\\\')
                cmd = f'wmic datafile where name="{escaped_path}" get Size,CreationDate,LastModified,Version /format:csv'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    analysis['tools_used'].append('wmic')
                    analysis['results']['wmic'] = result.stdout
            except:
                pass
        
        # CertUtil hash analysis
        if self.available_tools.get('certutil'):
            try:
                cmd = f'certutil -hashfile "{file_path}" SHA256'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    analysis['tools_used'].append('certutil')
                    # Extract hash from output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if len(line.strip()) == 64 and all(c in '0123456789abcdefABCDEF' for c in line.strip()):
                            analysis['results']['certutil_hash'] = line.strip()
                            break
            except:
                pass
        
        # PowerShell deep analysis
        if self.available_tools.get('powershell'):
            try:
                ps_script = f"""
                $file = "{file_path}"
                if (Test-Path $file) {{
                    $fileInfo = Get-Item $file
                    $hash = Get-FileHash $file -Algorithm SHA256
                    $content = Get-Content $file -Raw -ErrorAction SilentlyContinue -TotalCount 1000
                    
                    $result = @{{
                        Path = $file
                        Size = $fileInfo.Length
                        Hash = $hash.Hash
                        Created = $fileInfo.CreationTime.ToString()
                        Modified = $fileInfo.LastWriteTime.ToString()
                        Attributes = $fileInfo.Attributes.ToString()
                        IsReadOnly = $fileInfo.IsReadOnly
                        IsSystem = ($fileInfo.Attributes -band [System.IO.FileAttributes]::System) -ne 0
                        IsHidden = ($fileInfo.Attributes -band [System.IO.FileAttributes]::Hidden) -ne 0
                        HasContent = ($content -ne $null)
                        ContentLength = if ($content) {{ $content.Length }} else {{ 0 }}
                    }}
                    $result | ConvertTo-Json
                }}
                """
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    script_path = f.name
                
                try:
                    result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        analysis['tools_used'].append('powershell')
                        try:
                            analysis['results']['powershell'] = json.loads(result.stdout)
                        except:
                            analysis['results']['powershell'] = result.stdout
                finally:
                    try:
                        os.unlink(script_path)
                    except:
                        pass
            except:
                pass
        
        return analysis
    
    def analyze_processes(self):
        """Analyze running processes"""
        processes = []
        
        # Tasklist analysis
        if self.available_tools.get('tasklist'):
            try:
                result = subprocess.run('tasklist /fo csv /v', shell=True, 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = line.split('","')
                            if len(parts) >= 2:
                                processes.append({
                                    'name': parts[0].strip('"'),
                                    'pid': parts[1].strip('"'),
                                    'tool': 'tasklist'
                                })
            except:
                pass
        
        # PowerShell process analysis
        if self.available_tools.get('powershell'):
            try:
                ps_script = """
                Get-Process | Select-Object Id, ProcessName, Path, CPU, WorkingSet, StartTime | 
                    ConvertTo-Json
                """
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    script_path = f.name
                
                try:
                    result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        try:
                            ps_processes = json.loads(result.stdout)
                            if isinstance(ps_processes, list):
                                for proc in ps_processes:
                                    proc['tool'] = 'powershell'
                                    processes.append(proc)
                        except:
                            pass
                finally:
                    try:
                        os.unlink(script_path)
                    except:
                        pass
            except:
                pass
        
        return processes
    
    def analyze_network(self):
        """Analyze network connections"""
        connections = []
        
        # Netstat analysis
        if self.available_tools.get('netstat'):
            try:
                result = subprocess.run('netstat -ano', shell=True, 
                                      capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'TCP' in line or 'UDP' in line:
                            connections.append({
                                'line': line.strip(),
                                'tool': 'netstat'
                            })
            except:
                pass
        
        # PowerShell network analysis
        if self.available_tools.get('powershell'):
            try:
                ps_script = """
                Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess | 
                    ConvertTo-Json
                """
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    script_path = f.name
                
                try:
                    result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        try:
                            ps_connections = json.loads(result.stdout)
                            if isinstance(ps_connections, list):
                                for conn in ps_connections:
                                    conn['tool'] = 'powershell'
                                    connections.append(conn)
                        except:
                            pass
                finally:
                    try:
                        os.unlink(script_path)
                    except:
                        pass
            except:
                pass
        
        return connections
    
    def analyze_registry(self):
        """Analyze registry for threats"""
        registry_items = []
        
        # REG command analysis
        if self.available_tools.get('reg'):
            try:
                startup_keys = [
                    'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
                    'HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'
                ]
                
                for key in startup_keys:
                    try:
                        result = subprocess.run(f'reg query "{key}"', shell=True, 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            registry_items.append({
                                'key': key,
                                'data': result.stdout,
                                'tool': 'reg'
                            })
                    except:
                        pass
            except:
                pass
        
        # PowerShell registry analysis
        if self.available_tools.get('powershell'):
            try:
                ps_script = """
                $startupKeys = @(
                    "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                )
                
                $startupItems = @()
                foreach ($key in $startupKeys) {
                    if (Test-Path $key) {
                        $items = Get-ItemProperty $key
                        foreach ($item in $items.PSObject.Properties) {
                            if ($item.Name -ne "PSPath" -and $item.Name -ne "PSParentPath") {
                                $startupItems += @{
                                    Key = $key
                                    Name = $item.Name
                                    Value = $item.Value
                                }
                            }
                        }
                    }
                }
                $startupItems | ConvertTo-Json
                """
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    script_path = f.name
                
                try:
                    result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        try:
                            ps_registry = json.loads(result.stdout)
                            if isinstance(ps_registry, list):
                                for item in ps_registry:
                                    item['tool'] = 'powershell'
                                    registry_items.append(item)
                        except:
                            pass
                finally:
                    try:
                        os.unlink(script_path)
                    except:
                        pass
            except:
                pass
        
        return registry_items
    
    def analyze_services(self):
        """Analyze Windows services"""
        services = []
        
        # SC command analysis
        if self.available_tools.get('sc'):
            try:
                result = subprocess.run('sc query', shell=True, 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    services.append({
                        'data': result.stdout,
                        'tool': 'sc'
                    })
            except:
                pass
        
        # PowerShell services analysis
        if self.available_tools.get('powershell'):
            try:
                ps_script = """
                Get-Service | Select-Object Name, Status, DisplayName, StartType | 
                    ConvertTo-Json
                """
                with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                    f.write(ps_script)
                    script_path = f.name
                
                try:
                    result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        try:
                            ps_services = json.loads(result.stdout)
                            if isinstance(ps_services, list):
                                for svc in ps_services:
                                    svc['tool'] = 'powershell'
                                    services.append(svc)
                        except:
                            pass
                finally:
                    try:
                        os.unlink(script_path)
                    except:
                        pass
            except:
                pass
        
        return services

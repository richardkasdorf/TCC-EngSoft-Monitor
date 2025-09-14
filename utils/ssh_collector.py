import paramiko

PF_HOST = "192.168.2.1"
PF_USER = "admin"
PF_PASS = "pfsense"
INTERFACE = "em1"

def get_interface_stats():
    cmd = f"netstat -ib | grep {INTERFACE} | head -n 1"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PF_HOST, username=PF_USER, password=PF_PASS)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode().split()
    ssh.close()
    return int(output[7]), int(output[10])
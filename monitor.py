
"""
import paramiko
import time
import matplotlib.pyplot as plt

# Configurações de acesso ao pfSense
PF_HOST = "192.168.2.1"     # IP da LAN do seu pfSense
PF_USER = "admin"           # Usuário
PF_PASS = "pfsense"       # Senha
INTERFACE = "em0"           # Ajuste para a interface que deseja monitorar (LAN/WAN)

# Função para coletar estatísticas
def get_interface_stats():
    cmd = f"netstat -ib | grep {INTERFACE} | head -n 1"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PF_HOST, username=PF_USER, password=PF_PASS)

    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode().split()
    ssh.close()


    ibytes = int(output[7])   # Coluna 8 → bytes recebidos
    obytes = int(output[10])  # Coluna 11 → bytes enviados
    return ibytes, obytes


# listas para o gráfico
downloads = []
uploads = []
timestamps = []

ibytes_old, obytes_old = get_interface_stats()
time.sleep(5)

print("Coletando tráfego... pressione CTRL+C para parar.\n")

try:
    while True:
        ibytes_new, obytes_new = get_interface_stats()

        download_bps = (ibytes_new - ibytes_old) * 8 / 2
        upload_bps   = (obytes_new - obytes_old) * 8 / 2

        downloads.append(download_bps / (1024*1024))  # em Mbps
        uploads.append(upload_bps / (1024*1024))
        timestamps.append(time.strftime("%H:%M:%S"))

        print(f"↓ {downloads[-1]:.3f} Mbps | ↑ {uploads[-1]:.3f} Mbps")

        ibytes_old, obytes_old = ibytes_new, obytes_new
        time.sleep(5)

except KeyboardInterrupt:
    print("\nEncerrando coleta e plotando gráfico...")

    plt.figure(figsize=(10,5))
    plt.plot(timestamps, downloads, label="Download (Mbps)")
    plt.plot(timestamps, uploads, label="Upload (Mbps)")
    plt.xticks(rotation=45)
    plt.xlabel("Tempo")
    plt.ylabel("Mbps")
    plt.title("Consumo de Banda em Tempo Real")
    plt.legend()
    plt.tight_layout()
    plt.show()













from flask import Flask, render_template, jsonify
from utils.ssh_collector import get_interface_stats
import time

app = Flask(__name__)

ibytes_old = obytes_old = 0

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    global ibytes_old, obytes_old
    ibytes_new, obytes_new = get_interface_stats()
    if ibytes_old == 0:  # primeira medição
        ibytes_old, obytes_old = ibytes_new, obytes_new

    download_bps = (ibytes_new - ibytes_old) * 8 / 2
    upload_bps   = (obytes_new - obytes_old) * 8 / 2

    ibytes_old, obytes_old = ibytes_new, obytes_new

    return jsonify({
        "download": round(download_bps / (1024*1024), 3),
        "upload": round(upload_bps / (1024*1024), 3),
        "timestamp": time.strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
"""

from paramiko import SSHClient, AutoAddPolicy

ssh = SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect("192.168.2.1", username="admin", password="pfsense")

stdin, stdout, stderr = ssh.exec_command("netstat -ib | grep em1")
print(stdout.read().decode())


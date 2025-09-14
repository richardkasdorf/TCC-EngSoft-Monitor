
from flask import Flask, jsonify, render_template, request
import time, sqlite3, time, os, webbrowser
from utils.ssh_collector import get_interface_stats
from db.database import DB_PATH, init_db, save_to_db, get_history
from threading import Timer

app = Flask(__name__)

init_db()

last_rx, last_tx, last_time = 0, 0, time.time()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# -------------------------------------------------------------- #

# Consumo tempo real / Real ime consum

@app.route("/data")
def data():
    global last_rx, last_tx, last_time

    rx, tx = get_interface_stats()
    now = time.time()

    if last_rx == 0 and last_tx == 0:
        last_rx, last_tx, last_time = rx, tx, now
        return jsonify(download_mbps=0, upload_mbps=0)
    
    
    elapsed = now - last_time if last_time else 1

    download_mbps = ((rx - last_rx) * 8) / (elapsed * 1024 * 1024)
    upload_mbps   = ((tx - last_tx) * 8) / (elapsed * 1024 * 1024)

    last_rx, last_tx, last_time = rx, tx, now

    save_to_db(round(download_mbps, 2), round(upload_mbps, 2))

    return jsonify(
        download_mbps=round(download_mbps, 2),
        upload_mbps=round(upload_mbps, 2)
    )

# -------------------------------------------------------------- #

# Relatório de consumo por periodo / Consum report by period

@app.route("/report_data")
def report_data():
    start = request.args.get("start")
    end = request.args.get("end")

    
    if len(start) == 16:  
        start += ":00"
    if len(end) == 16:
        end += ":59"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, download_mbps, upload_mbps FROM traffic WHERE timestamp BETWEEN ? AND ?",
        (start, end)
    )
    rows = cursor.fetchall()
    conn.close()

    data = [{"time": r[0], "rx": r[1], "tx": r[2]} for r in rows]

    return jsonify(data)

# -------------------------------------------------------------- #

# Dashboard Estatistico / Stat Dashboard 

@app.route("/dashboard_data")
def dashboard_data():
    start = request.args.get("start")
    end = request.args.get("end")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if start and end:
        cursor.execute(
            "SELECT download_mbps, upload_mbps FROM traffic WHERE timestamp BETWEEN ? AND ?",
            (start, end)
        )
    else:
        cursor.execute("SELECT download_mbps, upload_mbps FROM traffic")

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"avg_download": 0, "avg_upload": 0,
                        "max_download": 0, "max_upload": 0})

    downloads = [r[0] for r in rows]
    uploads = [r[1] for r in rows]

    avg_download = sum(downloads) / len(downloads)
    avg_upload = sum(uploads) / len(uploads)
    max_download = max(downloads)
    max_upload = max(uploads)

    return jsonify({
        "avg_download": avg_download,
        "avg_upload": avg_upload,
        "max_download": max_download,
        "max_upload": max_upload
    })

# -------------------------------------------------------------- #

# Historico Grafico

@app.route("/dashboard_trend")
def dashboard_trend():
    start = request.args.get("start")
    end = request.args.get("end")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if start and end:
        cursor.execute(
            """
            SELECT DATE(timestamp), AVG(download_mbps), AVG(upload_mbps)
            FROM traffic
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
            """,
            (start, end)
        )
    else:
        cursor.execute(
            """
            SELECT DATE(timestamp), AVG(download_mbps), AVG(upload_mbps)
            FROM traffic
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp)
            """
        )

    rows = cursor.fetchall()
    conn.close()

    data = [{"date": r[0], "avg_download": r[1], "avg_upload": r[2]} for r in rows]
    return jsonify(data)

if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000")).start()


if __name__ == "__main__":
    app.run(debug=True)





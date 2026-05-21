from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'honeypot.db')

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # All attempts
    cursor.execute("SELECT timestamp, ip, username, password FROM attempts ORDER BY timestamp DESC")
    attempts = cursor.fetchall()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM attempts")
    total = cursor.fetchone()[0]

    # Top usernames
    cursor.execute("SELECT username, COUNT(*) as c FROM attempts GROUP BY username ORDER BY c DESC LIMIT 5")
    top_usernames = cursor.fetchall()

    # Top passwords
    cursor.execute("SELECT password, COUNT(*) as c FROM attempts GROUP BY password ORDER BY c DESC LIMIT 5")
    top_passwords = cursor.fetchall()

    # Top IPs
    cursor.execute("SELECT ip, COUNT(*) as c FROM attempts GROUP BY ip ORDER BY c DESC LIMIT 5")
    top_ips = cursor.fetchall()

    conn.close()
    return attempts, total, top_usernames, top_passwords, top_ips

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Honeypot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background: #0d0d0d; color: #00ff99; padding: 20px; }
        h1 { text-align: center; }
        .stats { display: flex; justify-content: center; gap: 40px; margin: 20px 0; }
        .stat-box { background: #1a1a1a; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-box h2 { font-size: 2em; margin: 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #333; text-align: left; }
        th { background: #1a1a1a; }
        tr:hover { background: #1a1a1a; }
        .charts { display: flex; gap: 20px; margin-top: 30px; }
        .chart-box { background: #1a1a1a; padding: 20px; border-radius: 8px; flex: 1; }
    </style>
</head>
<body>
    <h1>🍯 SSH Honeypot Dashboard</h1>

    <div class="stats">
        <div class="stat-box">
            <h2>{{ total }}</h2>
            <p>Total Attempts</p>
        </div>
        <div class="stat-box">
            <h2>{{ top_ips|length }}</h2>
            <p>Unique IPs</p>
        </div>
    </div>

    <div class="charts">
        <div class="chart-box">
            <h3>Top Usernames</h3>
            <canvas id="usernameChart"></canvas>
        </div>
        <div class="chart-box">
            <h3>Top Passwords</h3>
            <canvas id="passwordChart"></canvas>
        </div>
    </div>

    <h2>Recent Attempts</h2>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>IP</th>
            <th>Username</th>
            <th>Password</th>
        </tr>
        {% for a in attempts %}
        <tr>
            <td>{{ a[0] }}</td>
            <td>{{ a[1] }}</td>
            <td>{{ a[2] }}</td>
            <td>{{ a[3] }}</td>
        </tr>
        {% endfor %}
    </table>

    <script>
        new Chart(document.getElementById('usernameChart'), {
            type: 'bar',
            data: {
                labels: {{ top_usernames | map(attribute=0) | list | tojson }},
                datasets: [{ 
                    label: 'Attempts',
                    data: {{ top_usernames | map(attribute=1) | list | tojson }},
                    backgroundColor: '#00ff99'
                }]
            },
            options: { plugins: { legend: { labels: { color: '#00ff99' }}}, scales: { x: { ticks: { color: '#00ff99' }}, y: { ticks: { color: '#00ff99' }}}}
        });

        new Chart(document.getElementById('passwordChart'), {
            type: 'bar',
            data: {
                labels: {{ top_passwords | map(attribute=0) | list | tojson }},
                datasets: [{ 
                    label: 'Attempts',
                    data: {{ top_passwords | map(attribute=1) | list | tojson }},
                    backgroundColor: '#ff4444'
                }]
            },
            options: { plugins: { legend: { labels: { color: '#00ff99' }}}, scales: { x: { ticks: { color: '#00ff99' }}, y: { ticks: { color: '#00ff99' }}}}
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    attempts, total, top_usernames, top_passwords, top_ips = get_stats()
    return render_template_string(HTML,
        attempts=attempts,
        total=total,
        top_usernames=top_usernames,
        top_passwords=top_passwords,
        top_ips=top_ips
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
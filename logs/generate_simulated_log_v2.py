import random
from datetime import datetime, timedelta
import csv

users = ['tom', 'alice', 'bob', 'john', 'root', 'admin']
local_ips = [f'192.168.1.{i}' for i in range(2, 30)]
external_ips = [f'203.0.113.{i}' for i in range(2, 30)]
all_ips = local_ips + external_ips
ports = list(range(1024, 65535))

def assess_risk(user, ip, status):
    if user in ['root', 'admin'] and status == 'Failed':
        return 'high'
    if status == 'Failed' and ip.startswith('203.0.113.'):
        return 'medium'
    return 'low'

def generate_log_line(timestamp, user, ip, status, port):
    log = f"{timestamp.strftime('%b %d %H:%M:%S')} ubuntu sshd[{random.randint(1000,9999)}]: {status} password for {user} from {ip} port {port} ssh2"
    return log

def generate_logs(num_logs=200, txt_path="simulated_log.txt", csv_path="simulated_log.csv"):
    log_lines = []
    csv_rows = []
    now = datetime.now()

    for _ in range(num_logs):
        user = random.choice(users)
        ip = random.choice(all_ips)
        port = random.choice(ports)

        status = 'Failed' if user in ['root', 'admin'] else random.choices(['Accepted', 'Failed'], weights=[0.7, 0.3])[0]
        timestamp = now - timedelta(minutes=random.randint(0, 10000))
        risk = assess_risk(user, ip, status)

        line = generate_log_line(timestamp, user, ip, status, port)
        log_lines.append(line)
        csv_rows.append({
            'timestamp': timestamp.isoformat(),
            'user': user,
            'ip': ip,
            'status': status,
            'port': port,
            'risk_level': risk
        })

    with open(txt_path, "w") as f:
        f.write("\n".join(log_lines))

    with open(csv_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"[✓] Logs written to: {txt_path}")
    print(f"[✓] Labeled data written to: {csv_path}")

if __name__ == "__main__":
    generate_logs()

import random
from datetime import datetime, timedelta

users = ['tom', 'alice', 'bob', 'john', 'root', 'admin']
local_ips = [f'192.168.1.{i}' for i in range(2, 30)]
external_ips = [f'203.0.113.{i}' for i in range(2, 30)]
all_ips = local_ips + external_ips
ports = list(range(1024, 65535))

def generate_log_line(timestamp, user, ip, status, port):
    return f"{timestamp.strftime('%b %d %H:%M:%S')} ubuntu sshd[{random.randint(1000,9999)}]: {status} password for {user} from {ip} port {port} ssh2"

def generate_logs(num_logs=200, output_path="simulated_log.txt"):
    log_lines = []
    now = datetime.now()

    for _ in range(num_logs):
        user = random.choice(users)
        ip = random.choice(all_ips)
        port = random.choice(ports)

        if user in ['root', 'admin']:
            status = 'Failed'
        else:
            status = random.choices(['Accepted', 'Failed'], weights=[0.7, 0.3])[0]

        timestamp = now - timedelta(minutes=random.randint(0, 10000))
        log_line = generate_log_line(timestamp, user, ip, status, port)
        log_lines.append(log_line)

    with open(output_path, "w") as f:
        f.write("\n".join(log_lines))

    print(f"[✓] Generated {num_logs} log lines to '{output_path}'")

if __name__ == "__main__":
    generate_logs()

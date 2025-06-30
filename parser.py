import re
import pandas as pd
from datetime import datetime

# Regular expression for parsing raw SSH logs
LOG_PATTERN = re.compile(
    r'^(?P<month>\w{3}) (?P<day>\d{1,2}) (?P<time>\d{2}:\d{2}:\d{2}) .*sshd\[\d+\]: (?P<status>\w+) password for (?P<user>\w+) from (?P<ip>[\d.]+) port (?P<port>\d+) ssh2$'
)

# Parse raw log line into dictionary
def parse_log_line(line, year=None):
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    month_str = match.group('month')
    day = int(match.group('day'))
    time_str = match.group('time')
    month = datetime.strptime(month_str, '%b').month
    year = year or datetime.now().year

    timestamp_str = f"{year}-{month:02d}-{day:02d} {time_str}"
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

    return {
        'timestamp': timestamp,
        'user': match.group('user'),
        'ip': match.group('ip'),
        'status': match.group('status'),
        'port': int(match.group('port'))
    }

# Load and parse log file (.txt)
def load_logs_from_txt(file_path):
    logs = []
    with open(file_path, 'r') as f:
        for line in f:
            parsed = parse_log_line(line.strip())
            if parsed:
                logs.append(parsed)
    return pd.DataFrame(logs)

# Load structured log file (.csv)
def load_logs_from_csv(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Example usage
if __name__ == "__main__":
    txt_logs = load_logs_from_txt("logs/simulated_log.txt")
    print("[TXT] Parsed logs:", txt_logs.head())

    csv_logs = load_logs_from_csv("logs/simulated_log.csv")
    print("[CSV] Parsed logs:", csv_logs.head())

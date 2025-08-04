from datetime import datetime

# Function to get current timestamp
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Function to log messages
def log_message(message, file_path):
    timestamped_message = f"[{get_timestamp()}] {message}"
    with open(file_path, "a") as file:  # Append log instead of overwriting
        file.write(timestamped_message + "\n")
    print(timestamped_message)  # Also print to console


# TODO: make use of lib and better standardization (level: [Information][Warning][Error])
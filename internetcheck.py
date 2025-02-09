import socket
import subprocess

def check_internet(host="8.8.8.8", port=53, timeout=3):
    """
    Check for an internet connection by attempting to connect to a known host.
    
    Args:
        host (str): The host to connect to (default is Google's public DNS server).
        port (int): The port to use (default is 53, which is DNS).
        timeout (int): Timeout in seconds for the connection attempt.
        
    Returns:
        bool: True if the connection succeeds, False otherwise.
    """
    try:
        # Set the default timeout for new socket objects
        socket.setdefaulttimeout(timeout)
        # Create a new socket using IPv4 and TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except socket.error as err:
        print(f"Internet connection check failed: {err}")
        return False

def main():
    if check_internet():
        print("Internet connection detected. Executing the script...")
        # Replace 'otherscript.py' with the path to your Python script
        try:
            subprocess.run(["python", "driveget.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")
    else:
        print("No internet connection detected. Exiting.")

if __name__ == '__main__':
    main()

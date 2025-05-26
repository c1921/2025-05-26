import socket

def find_free_port(start_port=8080, max_tries=100):
    """查找可用的端口号"""
    for port in range(start_port, start_port + max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError('无法找到可用的端口')
import socket
import subprocess

# from http://stackoverflow.com/questions/3764291/checking-network-connection#3764660
def connection_available(host="8.8.8.8", port=80, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print(ex.message)
        return False

def call(command):
    output = subprocess.check_output(command.split(' '))
    encoded = output.decode('utf8').strip()

    return encoded

if __name__ == '__main__':
    salida = call('dropbox_uploader.sh share file7')

    print(salida.split(' ')[3])

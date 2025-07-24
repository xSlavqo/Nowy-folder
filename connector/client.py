# connector/client.py
import socket
import struct
import io
from PIL import Image

class PhoneConnector:
    """
    Klasa do zarządzania połączeniem i komunikacją z serwerem na telefonie.
    """
    def __init__(self, phone_ip, server_port):
        self.phone_ip = phone_ip
        self.server_port = server_port
        self.secret_key = "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"
        self.socket = None
        self._connect()

    def _connect(self):
        """Nawiązuje połączenie i przeprowadza autoryzację."""
        try:
            print(f"Connecting to {self.phone_ip}:{self.server_port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.phone_ip, self.server_port))
            print("Connected. Authenticating...")
            self.socket.sendall(f"{self.secret_key}\n".encode('utf-8'))
            print("Authentication successful.")
        except Exception as e:
            print(f"Failed to connect or authenticate: {e}")
            self.socket = None
            raise

    def _receive_all(self, length):
        """Pomocnicza funkcja do odbierania dokładnie określonej liczby bajtów."""
        data = bytearray()
        while len(data) < length:
            packet = self.socket.recv(length - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def get_screenshot(self, color=False):
        """
        Pobiera zrzut ekranu z telefonu.
        :param color: Jeśli True, prosi o obraz w kolorze. Domyślnie skala szarości.
        :return: Obiekt PIL Image lub None w przypadku błędu.
        """
        if not self.socket:
            print("Not connected.")
            return None
        
        try:
            if color:
                command = b"GET_SCREENSHOT COLOR\n"
                print("Requesting screenshot in COLOR mode...")
            else:
                command = b"GET_SCREENSHOT\n"
                print("Requesting screenshot in GRAYSCALE mode (default)...")

            self.socket.sendall(command)
            
            size_data = self._receive_all(4)
            if not size_data: raise ConnectionError("Failed to receive image size.")
            
            image_size = struct.unpack('>I', size_data)[0]
            image_data = self._receive_all(image_size)
            if not image_data: raise ConnectionError("Failed to receive image data.")

            return Image.open(io.BytesIO(image_data))
        except socket.timeout:
            print("Error: Socket timeout during get_screenshot.")
            self.close()
            return None
        except Exception as e:
            print(f"An error occurred while getting screenshot: {e}")
            return None

    def click(self, x, y):
        """Wysyła komendę kliknięcia na podane współrzędne."""
        if not self.socket:
            print("Not connected.")
            return
            
        try:
            command = f"CLICK {int(x)} {int(y)}\n"
            self.socket.sendall(command.encode('utf-8'))
        except Exception as e:
            print(f"An error occurred while sending click: {e}")

    def close(self):
        """Zamyka połączenie z serwerem."""
        if self.socket:
            self.socket.close()
            print("Connection closed.")
            self.socket = None

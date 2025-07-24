# main.py
import time
# Zaktualizowany import, aby odzwierciedlał nową, płaską strukturę
from connector.client import PhoneConnector

# --- Konfiguracja Bota ---
PHONE_IP = "192.168.1.9"  # Wpisz IP swojego telefonu
PHONE_PORT = 48151

class Bot:
    """
    Klasa bota zawierająca logikę i obiekt device.
    """
    def __init__(self):
        self.device = None
    
    def connect(self):
        """Nawiązuje połączenie z telefonem."""
        try:
            self.device = PhoneConnector(phone_ip=PHONE_IP, server_port=PHONE_PORT)
            print("Bot is running...")
            return True
        except Exception as e:
            print(f"Błąd podczas łączenia: {e}")
            return False
    
    def disconnect(self):
        """Zamyka połączenie z telefonem."""
        if self.device:
            self.device.close()
            self.device = None
            print("Bot has been shut down.")
    
    def run(self):
        """
        Główna funkcja zawierająca logikę bota.
        """
        try:
            if not self.connect():
                return
            
            # --- TUTAJ ZACZYNA SIĘ WŁAŚCIWA LOGIKA BOTA ---
            
            # Przykład: Zrób zrzut ekranu i kliknij w jeden punkt
            screen = self.device.get_screenshot()
            if screen:
                print("Screenshot captured. Performing an action.")
                self.device.click(500, 1200)
                time.sleep(2)
            
            print("Bot has finished its current task cycle.")

        except Exception as e:
            print(f"A critical error occurred in the main loop: {e}")
        finally:
            self.disconnect()

def bot():
    """
    Funkcja bota zwracająca instancję klasy Bot.
    """
    bot_instance = Bot()
    bot_instance.run()
    return bot_instance

def create_bot():
    """
    Tworzy i zwraca instancję bota bez uruchamiania głównej logiki.
    Przydatne do użycia z funkcjami locate.
    """
    bot_instance = Bot()
    if bot_instance.connect():
        return bot_instance
    return None

if __name__ == "__main__":
    bot()

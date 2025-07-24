import threading
import time

from PIL import Image, ImageChops
import numpy as np

from connector.client import PhoneConnector

PHONE_IP = "192.168.1.9"
PHONE_PORT = 48151

class ScreenshotHistory:
    def __init__(self, phone_ip, phone_port):
        self.device = PhoneConnector(phone_ip, phone_port)
        self.screenshots = []
        self.running = False
        self.thread = None

    def _capture_loop(self):
        while self.running:
            img = self.device.get_screenshot()
            if img:
                # Zachowaj oryginalny format bez konwersji
                self.screenshots.append(img)
                print(f"Captured screenshot #{len(self.screenshots)}")
            time.sleep(0.5)  # 0.5 sekundy między zrzutami

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.device.close()

    def save_common_pixels(self, output_path):
        if not self.screenshots:
            print("No screenshots to process.")
            return
        arrs = [np.array(img) for img in self.screenshots]
        base = arrs[0]
        # maska: True tam, gdzie WSZYSTKIE kanały RGBA są identyczneq we wszystkich obrazach
        mask = np.ones(base.shape[:2], dtype=bool)
        for arr in arrs[1:]:
            mask &= np.all(arr == base, axis=-1)
        result = base.copy()
        # Ustaw przezroczystość tam, gdzie piksele się różnią
        result[~mask, 3] = 0
        out_img = Image.fromarray(result, 'RGBA')
        out_img.save(output_path)
        print(f"Saved result to {output_path}")

if __name__ == "__main__":
    import keyboard
    sh = ScreenshotHistory(PHONE_IP, PHONE_PORT)
    print("Rozpoczynam przechwytywanie zrzutów ekranu. Wciśnij 'q', aby zakończyć i zapisać wynik.")
    sh.start()
    keyboard.wait('q')
    sh.stop()
    sh.save_common_pixels('common_pixels.png') 
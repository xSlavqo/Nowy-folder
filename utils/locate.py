import os
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

from connector.client import PhoneConnector

# Globalny cache dla wzorców
_template_cache: Dict[str, Tuple[np.ndarray, Optional[np.ndarray]]] = {}


def _load_template(template_path: str) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Ładuje wzorzec w skali szarości i nakłada maskę przezroczystości.
    
    Args:
        template_path: Ścieżka do pliku wzorca
        
    Returns:
        Krotka (wzorzec, maska) gdzie maska może być None
    """
    # Wczytaj obraz z kanałem alpha (RGBA)
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    
    if template is None:
        raise ValueError(f"Nie można wczytać obrazu: {template_path}")
    
    # Sprawdź czy obraz ma kanał alpha
    if len(template.shape) > 2 and template.shape[-1] == 4:
        # Rozdziel kanały RGBA
        b, g, r, a = cv2.split(template)
        
        # Utwórz maskę z kanału alpha (0 = przezroczyste, 255 = nieprzezroczyste)
        mask = a
        
        # Zwróć obraz w skali szarości (pierwszy kanał) i maskę
        return template[:, :, 0], mask
    else:
        # Obraz bez kanału alpha - zwróć bez maski
        return template, None


def _get_template(template_path: str) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Pobiera wzorzec z cache lub ładuje go z dysku.
    """
    if template_path not in _template_cache:
        _template_cache[template_path] = _load_template(template_path)
    
    return _template_cache[template_path]


def _get_device_from_bot(bot_instance) -> PhoneConnector:
    """
    Wyciąga obiekt device z instancji bota.
    """
    if hasattr(bot_instance, 'device') and bot_instance.device is not None:
        return bot_instance.device
    
    if isinstance(bot_instance, PhoneConnector):
        return bot_instance
    
    raise ValueError("Nieprawidłowy typ bota. Oczekiwano funkcji bot() z atrybutem device lub PhoneConnector")


def _find_best_match_in_folder(bot_instance, folder_path: str, threshold: float = 0.8) -> Optional[Tuple[str, Tuple[int, int], float]]:
    """
    Wyszukuje najlepszy wzorzec w folderze z obrazami.
    """
    device = _get_device_from_bot(bot_instance)
    
    # Pobierz zrzut ekranu z telefonu w skali szarości
    screenshot = device.get_screenshot(color=False)
    if screenshot is None:
        print("Nie udało się pobrać zrzutu ekranu")
        return None
    
    # Konwertuj PIL Image do numpy array
    screenshot_np = np.array(screenshot)
    
    best_match = None
    best_score = 0.0
    
    # Sprawdź wszystkie pliki .png w folderze
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(folder_path, filename)
            
            try:
                # Pobierz wzorzec i maskę
                template, mask = _get_template(file_path)
                
                # Wykonaj dopasowanie wzorca
                if mask is not None:
                    result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCORR_NORMED, mask=mask)
                else:
                    result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
                
                # Znajdź najlepsze dopasowanie dla tego wzorca
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= threshold and max_val > best_score:
                    # Oblicz środek wzorca
                    h, w = template.shape
                    center_x = max_loc[0] + w // 2
                    center_y = max_loc[1] + h // 2
                    
                    best_match = (filename, (center_x, center_y), max_val)
                    best_score = max_val
                    
            except Exception as e:
                print(f"Błąd podczas przetwarzania {filename}: {e}")
                continue
    
    return best_match


def locate(bot_instance, template_path: str, threshold: float = 0.95) -> Optional[Tuple[int, int]]:
    """
    Wyszukuje wzorzec na aktualnym zrzucie ekranu z telefonu.
    
    Args:
        bot_instance: Instancja bota (funkcja bot() z main.py lub PhoneConnector)
        template_path: Ścieżka do pliku wzorca .png lub folderu z obrazami .png
        threshold: Próg dopasowania (0.0 - 1.0)
        
    Returns:
        Krotka (x, y) z koordynatami środka wzorca lub None jeśli nie znaleziono
    """
    device = _get_device_from_bot(bot_instance)
    
    # Sprawdź czy to folder czy pojedynczy plik
    if os.path.isdir(template_path):
        # To folder - znajdź najlepszy wzorzec
        result = _find_best_match_in_folder(bot_instance, template_path, threshold)
        if result:
            filename, coordinates, score = result
            print(f"Znaleziono najlepszy wzorzec: {filename} (dopasowanie: {score:.3f})")
            return coordinates
        return None
    
    # To pojedynczy plik
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Plik wzorca nie istnieje: {template_path}")
    
    if not template_path.lower().endswith('.png'):
        raise ValueError(f"Plik musi być w formacie .png: {template_path}")
    
    # Pobierz zrzut ekranu z telefonu w skali szarości
    screenshot = device.get_screenshot(color=False)
    if screenshot is None:
        print("Nie udało się pobrać zrzutu ekranu")
        return None
    
    # Konwertuj PIL Image do numpy array
    screenshot_np = np.array(screenshot)
    
    # Pobierz wzorzec i maskę
    template, mask = _get_template(template_path)
    
    # Wykonaj dopasowanie wzorca
    if mask is not None:
        # Użyj maski przezroczystości
        result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCORR_NORMED, mask=mask)
    else:
        # Bez maski
        result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
    
    # Znajdź najlepsze dopasowanie
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        # Oblicz środek wzorca
        h, w = template.shape
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y)
    
    return None


def locate_and_click(bot_instance, template_path: str, threshold: float = 0.95, click: bool = True) -> Optional[Tuple[int, int]]:
    """
    Wyszukuje wzorzec i opcjonalnie klika w znalezioną pozycję.
    
    Args:
        bot_instance: Instancja bota (funkcja bot() z main.py lub PhoneConnector)
        template_path: Ścieżka do pliku wzorca .png lub folderu z obrazami .png
        threshold: Próg dopasowania (0.0 - 1.0)
        click: Czy kliknąć w znalezioną pozycję
        
    Returns:
        Krotka (x, y) z koordynatami lub None jeśli nie znaleziono
    """
    device = _get_device_from_bot(bot_instance)
    coordinates = locate(bot_instance, template_path, threshold)
    
    if coordinates and click:
        x, y = coordinates
        print(f"Klikam w pozycję: ({x}, {y})")
        device.click(x, y)
    
    return coordinates 
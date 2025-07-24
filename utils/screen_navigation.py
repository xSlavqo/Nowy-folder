import os
from typing import Optional, Tuple
from .locate import locate, locate_and_click

# Główne ścieżki do obrazów
CITY_IMAGE = os.path.join("images", "city.png")
MAP_IMAGE = os.path.join("images", "map.png")


def navigate_to_city(bot_instance) -> bool:
    """
    Nawiguje do ekranu miasta.
    
    Args:
        bot_instance: Instancja bota z obiektem device
        
    Returns:
        bool: True jeśli udało się przejść do miasta, False w przeciwnym razie
    """
    # Sprawdź czy jesteśmy już w mieście
    if locate(bot_instance, CITY_IMAGE, threshold=0.8):
        print("Jesteśmy już w mieście")
        return True
    
    # Sprawdź czy jesteśmy na mapie
    if locate(bot_instance, MAP_IMAGE, threshold=0.8):
        print("Jesteśmy na mapie, przełączam do miasta")
        # Kliknij na mapę aby przełączyć do miasta
        if locate_and_click(bot_instance, MAP_IMAGE, threshold=0.8):
            return True
    
    # Jeśli nie ma ani mapy ani miasta, spróbuj przycisk powrotu
    print("Nie znaleziono ani mapy ani miasta, próbuję przycisk powrotu")
    return _try_back_button(bot_instance)


def navigate_to_map(bot_instance) -> bool:
    """
    Nawiguje do ekranu mapy.
    
    Args:
        bot_instance: Instancja bota z obiektem device
        
    Returns:
        bool: True jeśli udało się przejść do mapy, False w przeciwnym razie
    """
    # Sprawdź czy jesteśmy już na mapie
    if locate(bot_instance, MAP_IMAGE, threshold=0.8):
        print("Jesteśmy już na mapie")
        return True
    
    # Sprawdź czy jesteśmy w mieście
    if locate(bot_instance, CITY_IMAGE, threshold=0.8):
        print("Jesteśmy w mieście, przełączam do mapy")
        # Kliknij na miasto aby przełączyć do mapy
        if locate_and_click(bot_instance, CITY_IMAGE, threshold=0.8):
            return True
    
    # Jeśli nie ma ani mapy ani miasta, spróbuj przycisk powrotu
    print("Nie znaleziono ani mapy ani miasta, próbuję przycisk powrotu")
    return _try_back_button(bot_instance)


def navigate_to_mainscreen(bot_instance) -> bool:
    """
    Nawiguje do głównego ekranu (miasto lub mapa, w zależności co jest pierwsze).
    
    Args:
        bot_instance: Instancja bota z obiektem device
        
    Returns:
        bool: True jeśli udało się przejść do głównego ekranu, False w przeciwnym razie
    """
    # Sprawdź czy jesteśmy już na głównym ekranie
    if locate(bot_instance, CITY_IMAGE, threshold=0.8):
        print("Jesteśmy już na głównym ekranu (miasto)")
        return True
    
    if locate(bot_instance, MAP_IMAGE, threshold=0.8):
        print("Jesteśmy już na głównym ekranu (mapa)")
        return True
    
    # Jeśli nie ma ani mapy ani miasta, spróbuj przycisk powrotu
    print("Nie znaleziono głównego ekranu, próbuję przycisk powrotu")
    return _try_back_button(bot_instance)


def _try_back_button(bot_instance) -> bool:
    """
    Próbuje użyć przycisku powrotu aby wrócić do głównego ekranu.
    
    Args:
        bot_instance: Instancja bota z obiektem device
        
    Returns:
        bool: True jeśli udało się wrócić, False w przeciwnym razie
    """
    try:
        # Pobierz obiekt device
        device = bot_instance.device if hasattr(bot_instance, 'device') else bot_instance
        
        # Wyślij komendę powrotu do serwera
        # Zakładam, że device ma metodę send_command lub podobną
        if hasattr(device, 'send_command'):
            device.send_command("BACK")
            print("Wysłano komendę powrotu")
            return True
        elif hasattr(device, 'socket'):
            # Jeśli device to PhoneConnector, wyślij przez socket
            command = "BACK\n"
            device.socket.sendall(command.encode('utf-8'))
            print("Wysłano komendę powrotu przez socket")
            return True
        else:
            print("Nie można wysłać komendy powrotu - brak odpowiedniej metody")
            return False
            
    except Exception as e:
        print(f"Błąd podczas wysyłania komendy powrotu: {e}")
        return False


def get_current_screen(bot_instance) -> Optional[str]:
    """
    Sprawdza na jakim ekranie obecnie się znajdujemy.
    
    Args:
        bot_instance: Instancja bota z obiektem device
        
    Returns:
        str: 'city', 'map' lub None jeśli nie rozpoznano
    """
    if locate(bot_instance, CITY_IMAGE, threshold=0.8):
        return "city"
    elif locate(bot_instance, MAP_IMAGE, threshold=0.8):
        return "map"
    else:
        return None 
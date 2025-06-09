import arcade
import random
import math
import time
from typing import List, Optional, Dict
import socket
import threading
import json
import os
import pyglet
import uuid

# Настройки игры
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
CARD_WIDTH = 80
CARD_HEIGHT = 116
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
MAX_PLAYERS_PER_LOBBY = 2

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}

# Настройки сети
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 4096
# Добавляем в начало файла, после импортов
LOCALIZATION = {
    "en": {
        "game_title": "DURAK ONLINE",
        "play_vs_bot": "Play vs Bot",
        "create_lobby": "Create Lobby",
        "join_lobby": "Join Lobby",
        "settings": "Settings",
        "exit": "Exit",
        "back": "Back",
        "player": "Player",
        "version": "v1.0",
        "trump": "Trump",
        "phase": "Phase",
        "cards_left": "Cards left",
        "play": "PLAY",
        "pass": "PASS",
        "invalid_move": "Invalid move",
        "you_take_cards": "You take cards",
        "card_played": "Card played",
        "wait_turn_end": "Wait for turn end",
        "victory": "VICTORY",
        "winner": "Winner",
        "return": "Return",
        "toggle_fullscreen": "Toggle Fullscreen",
        "sound_on_off": "Sound On/Off",
        "switch_monitor": "Switch Monitor",
        "change_resolution": "Change Resolution",
        "current_monitor": "Current Monitor",
        "current_resolution": "Current Resolution",
        "select_resolution": "Select resolution",
        "lobby_name": "Lobby Name",
        "available_lobbies": "Available Lobbies",
        "no_lobbies": "No lobbies available",
        "refresh": "Refresh",
        "join": "Join",
        "start_game": "Start Game",
        "leave_lobby": "Leave Lobby",
        "players": "PLAYERS",
        "load_background": "Load Custom Background",
        "enter_path": "Enter path to background image",
        "load": "Load",
        "background_loaded": "Background loaded successfully",
        "background_error": "Error loading background",
        "enter_path_first": "Enter path to background file",
        "create": "Create",
        "game_forced_start": "Game started by lobby creator",
        "game_started": "Game started",
        "player_timeout": "Player timeout - passing turn"
    },
    "ru": {
        "game_title": "ДУРАК ОНЛАЙН",
        "play_vs_bot": "Играть с ботом",
        "create_lobby": "Создать лобби",
        "join_lobby": "Присоединиться",
        "settings": "Настройки",
        "exit": "Выход",
        "back": "Назад",
        "player": "Игрок",
        "version": "v1.0",
        "trump": "Козырь",
        "phase": "Фаза",
        "cards_left": "Карт осталось",
        "play": "ИГРАТЬ",
        "pass": "ПАС",
        "invalid_move": "Недопустимый ход",
        "you_take_cards": "Вы пасуете и забираете карты",
        "card_played": "Карта сыграна",
        "wait_turn_end": "Подождите завершения хода",
        "victory": "ПОБЕДА",
        "winner": "Победитель",
        "return": "Вернуться",
        "toggle_fullscreen": "Полный экран",
        "sound_on_off": "Звук Вкл/Выкл",
        "switch_monitor": "Сменить монитор",
        "change_resolution": "Изменить разрешение",
        "current_monitor": "Текущий монитор",
        "current_resolution": "Текущее разрешение",
        "select_resolution": "Выберите разрешение",
        "lobby_name": "Название лобби",
        "available_lobbies": "Доступные лобби",
        "no_lobbies": "Нет доступных лобби",
        "refresh": "Обновить",
        "join": "Войти",
        "start_game": "Начать игру",
        "leave_lobby": "Покинуть лобби",
        "players": "ИГРОКИ",
        "load_background": "Загрузить фон",
        "enter_path": "Введите путь к изображению",
        "load": "Загрузить",
        "background_loaded": "Фон успешно загружен!",
        "background_error": "Ошибка загрузки фона",
        "enter_path_first": "Введите путь к файлу фона",
        "create": "Создать",
        "game_forced_start": "Игра начата принудительно создателем лобби",
        "game_started": "Игра начинается!",
        "player_timeout": "Игрок не успел - переход хода"
    }
}
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_default_sounds()
        self.enabled = True
        
    def load_default_sounds(self):
        """Загрузка стандартных звуков"""
        try:
            self.sounds["card_place"] = arcade.load_sound("sounds/card_place.mp3")
            self.sounds["button_click"] = arcade.load_sound("sounds/button_click.wav")
            # self.sounds["win"] = arcade.load_sound("sounds/win.mp3")
        except:
            print("Не удалось загрузить стандартные звуки. Убедитесь, что папка sounds существует")
            
    def load_custom_sound(self, sound_type, file_path):
        """Загрузка пользовательского звука"""
        try:
            if os.path.exists(file_path):
                self.sounds[sound_type] = arcade.load_sound(file_path)
                print(f"Пользовательский звук {sound_type} загружен успешно")
                return True
            else:
                print(f"Файл {file_path} не найден")
                return False
        except Exception as e:
            print(f"Ошибка загрузки звука: {e}")
            return False
        

    def toggle_sound(self):
        self.enabled = not self.enabled
        self.set_volume(1.0 if self.enabled else 0.0)



    def play_sound(self, sound_type):
        """Воспроизведение звука"""
        if sound_type in self.sounds and self.enabled:
            arcade.play_sound(self.sounds[sound_type])
            
    def set_volume(self, volume):
        """Установка громкости для всех звуков"""
        for sound in self.sounds.values():
            sound.volume = volume

class BackgroundManager:
    def __init__(self):
        self.background = None
        self.custom_background = None
        self.game_background = None
        
    def load_default_background(self):
        """Загрузка стандартного фона"""
        try:
            self.background = arcade.load_texture("card/default_background.jpg")
        except:
            print("Не удалось загрузить стандартный фон. Будет использован цветной фон")
            self.background = None
            
    def load_custom_background(self, file_path):
        """Загрузка пользовательского фона"""
        try:
            if os.path.exists(file_path):
                self.custom_background = arcade.load_texture(file_path)
                print("Пользовательский фон загружен успешно")
                return True
            else:
                print(f"Файл {file_path} не найден")
                return False
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")
            return False
            
    def draw(self):
        """Отрисовка фона"""
        if self.custom_background:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.custom_background)
        elif self.background:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        else:
            arcade.draw_lrtb_rectangle_filled(0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, arcade.color.DARK_GREEN)
    
    def draw_menu(self):
        """Отрисовка фона для меню"""
        self.draw()  # Или добавьте специальную логику для меню
    
    def draw_game(self):
        """Отрисовка фона для игры"""
        self.draw()  # Или добавьте специальную логику для игры

class NetworkManager:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.message_queue = []
        
    def connect(self, host, port):
        try:
            self.socket.connect((host, port))
            self.connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if data:
                    message = json.loads(data.decode())
                    self.message_queue.append(message)
            except Exception as e:
                print(f"Receive error: {e}")
                self.connected = False
    
    def send_message(self, message: Dict):
        if not self.connected:
            print("Попытка отправить сообщение без подключения!")
            return False
            
        try:
            print("Отправка сообщения:", message)  # Логирование
            self.socket.sendall(json.dumps(message).encode())
            return True
        except Exception as e:
            print(f"Ошибка отправки: {e}")
            self.connected = False
            return False

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.key = f"{rank}_{suit}"
        self.face_up = False
        self.texture = None
        try:
            print(f"Пытаюсь загрузить текстуру для карты: card/{self.key}.png")  # Отладочное сообщение
            self.texture = arcade.load_texture(f"card/{self.key}.png")
            print("Текстура успешно загружена")  # Отладочное сообщение
        except Exception as e:
            print(f"Ошибка загрузки текстуры карты: {e}")  # Отладочное сообщение
            self.texture = arcade.load_texture("card/card_back.png")
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.angle = 0
        self.face_up = False
        self.selected = False
        self.animation_progress = 0
        self.animation_type = None  # 'throw', 'deal', None
        self.animation_start = (0, 0)
        self.animation_time = 0

    def start_animation(self, anim_type, start_pos):
        self.animation_type = anim_type
        self.animation_start = start_pos
        self.animation_time = 0

    def update(self):
        self.animation_time += 0.05
        
        if self.animation_type == 'throw':
            progress = min(1, self.animation_time * 2)
            if progress < 1:
                # Прямое движение в центр стола
                center_x = SCREEN_WIDTH // 2
                center_y = SCREEN_HEIGHT // 2
                self.x = self.animation_start[0] + (center_x - self.animation_start[0]) * progress
                self.y = self.animation_start[1] + (center_y - self.animation_start[1]) * progress
        else:
            # Обычное плавное перемещение
            if self.animation_progress < 1:
                self.animation_progress += 0.05
                self.x = self.x + (self.target_x - self.x) * 0.1
                self.y = self.y + (self.target_y - self.y) * 0.1
                if abs(self.target_x - self.x) < 1 and abs(self.target_y - self.y) < 1:
                    self.animation_progress = 1
                    self.x = self.target_x
                    self.y = self.target_y
                
    def draw(self):
        if self.texture:
            arcade.draw_texture_rectangle(self.x, self.y, CARD_WIDTH, CARD_HEIGHT, 
                                      self.texture if self.face_up else arcade.load_texture("card/card_back.png"), 
                                      self.angle)
        if self.selected:
            arcade.draw_rectangle_outline(self.x, self.y, CARD_WIDTH+10, CARD_HEIGHT+10, 
                                       arcade.color.GOLD, 2)

class Player:
    def __init__(self, idx: int, name: str, is_human: bool = False):
        self.idx = idx
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []
        self.is_attacking = False
        self.is_defending = False
        
    def add_card(self, card: Card):
        self.hand.append(card)
        # Свои карты всегда видны
        card.face_up = self.is_human
        
    def play_card(self, card_idx: int) -> Optional[Card]:
        if 0 <= card_idx < len(self.hand):
            card = self.hand.pop(card_idx)
            return card
        return None

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.deck: List[Card] = []
        self.field: List[Card] = []
        self.trump_suit: Optional[str] = None
        self.current_player_idx = 0
        self.game_phase = "attack"  # "attack", "defense", "throw"
        self.attacker_idx = 0  # Индекс основного атакующего игрока
        self.winner = None
        self.last_move_time = time.time()
        self.move_timeout = 15  # секунд на ход
        
    def init_game(self, players_info: List[Dict], trump_suit: str, your_index: int):
        self.players = [Player(i, info["name"], info.get("is_you", False)) for i, info in enumerate(players_info)]
        self.trump_suit = trump_suit
        
        # Создаем колоду и перемешиваем
        self.deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.deck)
        
        # Раздача карт с правильным позиционированием
        for _ in range(6):
            for i, player in enumerate(self.players):
                if self.deck:
                    card = self.deck.pop()
                    player.add_card(card)
                    # Устанавливаем начальную позицию карты (центр экрана)
                    card.x = SCREEN_WIDTH // 2
                    card.y = SCREEN_HEIGHT // 2
                    # Целевая позиция будет установлена в position_cards
                    card.target_x = 0
                    card.target_y = 0
        
    def determine_first_player(self):
        min_trump = None
        for i, player in enumerate(self.players):
            for card in player.hand:
                if card.suit == self.trump_suit:
                    if min_trump is None or RANK_VALUES[card.rank] < RANK_VALUES[min_trump.rank]:
                        min_trump = card
                        self.current_player_idx = i
                        
    def can_beat(self, attacking_card: Card, defending_card: Card) -> bool:
        if defending_card.suit == self.trump_suit and attacking_card.suit != self.trump_suit:
            return True
        if defending_card.suit == attacking_card.suit:
            return RANK_VALUES[defending_card.rank] > RANK_VALUES[attacking_card.rank]
        return False
    
    def is_valid_defense(self, card: Card) -> bool:
        """Проверка валидности карты для защиты"""
        if not self.field or len(self.field) % 2 != 1:
            return False  # Нет карты для отбития или нечетное количество карт
        
        last_attack = self.field[-1]
        return self.can_beat(last_attack, card)
    
    def is_valid_throw(self, card: Card) -> bool:
        """Проверка валидности карты для подкидывания"""
        if not self.field:
            return False
        return any(card.rank == f.rank for f in self.field)
    
    def is_valid_attack(self, card: Card) -> bool:
        """Проверка валидности карты для атаки"""
        if not self.field:
            return True  # Первая карта в атаке - любая
        return any(card.rank == f.rank for f in self.field)
        
    def is_valid_move(self, card: Card, player_idx: int) -> bool:
        if self.game_phase == "attack":
            if not self.field:
                return True
            return any(card.rank == f.rank for f in self.field)
        elif self.game_phase == "defense":
            if len(self.field) % 2 == 1:
                attacking_card = self.field[-1]
                return self.can_beat(attacking_card, card)
        return False
        
    def make_move(self, player_idx: int, card_idx: int) -> bool:
        if player_idx != self.current_player_idx:
            return False
            
        player = self.players[player_idx]
        if card_idx < 0 or card_idx >= len(player.hand):
            return False
            
        card = player.hand[card_idx]
        
        # Проверка валидности хода в зависимости от фазы
        if self.game_phase == "attack" and not self.is_valid_attack(card):
            return False
        elif self.game_phase == "defense" and not self.is_valid_defense(card):
            return False
        elif self.game_phase == "throw" and not self.is_valid_throw(card):
            return False
            
        played_card = player.play_card(card_idx)
        if played_card:
            self.field.append(played_card)
            self.last_move_time = time.time()
            played_card.face_up = True
            
            # Логика перехода между фазами
            if self.game_phase == "attack":
                self.game_phase = "defense"
                self.current_player_idx = (player_idx + 1) % len(self.players)
                
            elif self.game_phase == "defense":
                if len(self.field) % 2 == 0:  # Четное количество карт = все отбито
                    self.game_phase = "throw"
                    self.current_player_idx = self.attacker_idx
                else:
                    self.current_player_idx = player_idx  # Остаемся у того же игрока
                    
            elif self.game_phase == "throw":
                self.game_phase = "defense"
                self.current_player_idx = (self.attacker_idx + 1) % len(self.players)
                
            return True
        return False
        
    def pass_move(self, player_idx: int) -> bool:
        if player_idx != self.current_player_idx:
            return False
            
        if self.game_phase == "defense":
            # Забрать карты должен защищающийся игрок (тот, кто пасует)
            taking_player = self.players[player_idx]
            taking_player.hand.extend(self.field)
            for card in self.field:
                card.face_up = False  # Скрываем карты, которые забирает игрок
            self.field.clear()
            self.refill_hands()
            
            # Переход хода
            self.attacker_idx = (self.attacker_idx + 1) % len(self.players)
            self.current_player_idx = self.attacker_idx
            self.game_phase = "attack"
            return True
            
        elif self.game_phase == "throw":
            # Завершение кона
            self.field.clear()
            self.refill_hands()
            
            # Переход хода следующему игроку
            self.attacker_idx = (self.attacker_idx + 1) % len(self.players)
            self.current_player_idx = self.attacker_idx
            self.game_phase = "attack"
            return True
            
        return False

        
    def refill_hands(self):
        # Сначала добирает атакующий, затем защищающийся
        players_order = [
            self.attacker_idx,
            (self.attacker_idx + 1) % len(self.players)
        ]
        
        for player_idx in players_order:
            player = self.players[player_idx]
            while len(player.hand) < 6 and self.deck:
                card = self.deck.pop()
                player.add_card(card)
                # Устанавливаем начальную позицию карты (из колоды)
                card.x = SCREEN_WIDTH * 0.1  # Позиция колоды
                card.y = SCREEN_HEIGHT // 2
                # Целевая позиция будет установлена в position_cards
                card.target_x = 0
                card.target_y = 0
                # Карты бота должны быть рубашкой вверх
                if not player.is_human:
                    card.face_up = False

                
    def check_game_over(self):
        for i, player in enumerate(self.players):
            if not player.hand:
                self.winner = i
                return True
        return False

class Button:
    def __init__(self, x, y, width, height, text, action=None, parent=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.hovered = False
        self.active = True
        self.texture_normal = None
        self.texture_hover = None
        self.parent = parent  # Добавляем атрибут parent 
        
    def draw(self):
        # Use parent textures if available, otherwise use default colors
        normal_texture = (self.texture_normal or 
                        (self.parent.ui_textures["button_normal"] if self.parent and "button_normal" in self.parent.ui_textures 
                        else None))
        hover_texture = (self.texture_hover or 
                        (self.parent.ui_textures["button_hover"] if self.parent and "button_hover" in self.parent.ui_textures 
                        else None))
        
        if self.hovered and hover_texture:
            arcade.draw_texture_rectangle(self.x, self.y, self.width, self.height, hover_texture)
        elif normal_texture:
            arcade.draw_texture_rectangle(self.x, self.y, self.width, self.height, normal_texture)
        else:
            # Fallback to simple colored rectangle if no textures available
            color = (200, 200, 200, 200) if self.hovered else (100, 100, 100, 200)
            arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, color)
        
        text_color = arcade.color.GOLD if self.hovered else arcade.color.WHITE
        arcade.draw_text(self.text, self.x, self.y, text_color, 20,
                        anchor_x="center", anchor_y="center", 
                        font_name=self.parent.minecraft_font_name if self.parent else None)
        
    def check_hover(self, x, y):
        if not self.active:
            self.hovered = False
            return False
            
        self.hovered = (
            abs(x - self.x) <= self.width/2 and 
            abs(y - self.y) <= self.height/2
        )
        return self.hovered
        
    def check_click(self, x, y):
        return (self.hovered and self.action)

class GameUI(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Durka Online", fullscreen=False, resizable=True)
        self.set_min_size(800, 600)  # Минимальный размер окна
        self.set_fullscreen(False)
        self.current_language = "ru"
        self.return_button_hovered = False
        self.game_state: Optional[GameState] = None
        self.network = NetworkManager()
        self.is_animating = False
        self.winner_window = None
        self.resolution_dialog = None
        self.resolution_buttons = []
        self.current_monitor_name = ""
        self.sound_manager = SoundManager()
        self.background_manager = BackgroundManager()
        self.background_manager.load_default_background()
        self.player_positions = []
        self.selected_card_idx = -1
        self.message = ""
        self.font_size = 20
        self.font_loaded = False
        self.current_screen = "main_menu"  # "main_menu", "lobby_list", "lobby", "game", "settings"
        self.lobbies = []
        self.lobby_buttons = []
        # загрузка шрифта
        self.default_font = None
        self.minecraft_font = None
        self.current_font = "default"  # "default" или "minecraft"
        self.load_fonts()
        # Загрузка текстур для UI
        self.ui_textures = {
            "button_normal": arcade.make_soft_square_texture(BUTTON_WIDTH, (100, 100, 100, 200)),
            "button_hover": arcade.make_soft_square_texture(BUTTON_WIDTH, (200, 200, 200, 200)),
            "panel": arcade.make_soft_square_texture(100, (0, 0, 0, 180))
            }
        
        # Настройки звука
        self.master_volume = 1.0  # Громкость от 0.0 до 1.0
        self.volume_slider = {
            "x": SCREEN_WIDTH//2,
            "y": SCREEN_HEIGHT//2,
            "width": 300,
            "height": 20,
            "dragging": False,
            "min_x": SCREEN_WIDTH//2 - 150,
            "max_x": SCREEN_WIDTH//2 + 150,
            "knob_x": SCREEN_WIDTH//2 - 150 + 300 * 1.0  # Начальное положение соответствует громкости 1.0
        }
        self.sound_manager.set_volume(self.master_volume)  # Применяем начальную громкость


        # Получаем список мониторов
        self.monitors = pyglet.canvas.get_display().get_screens()
        self.current_monitor = 0  # Индекс текущего монитора


        self.minecraft_font_name = None  # Имя шрифта Minecraft, если загружен    
        self.current_lobby = None
        # Генерация уникального имени игрока
        self.player_name = f"Player_{int(time.time())}_{random.randint(1000, 9999)}"
        self.input_text = ""
        self.active_input = None
        # Например, в setup_main_menu:
        self.buttons = [
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                "Play vs Bot", lambda: self.setup_single_player_game(), self),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Create Lobby", lambda: self.setup_create_lobby(), self),
        ]
        self.confirmation_dialog = None
        self.setup_main_menu()
    def set_language(self, language: str):
            if language in LOCALIZATION:
                self.current_language = language
                # Обновляем текст кнопок при смене языка
                if self.current_screen == "main_menu":
                    self.setup_main_menu()
                elif self.current_screen == "settings":
                    self.setup_settings()
    
    def tr(self, key: str) -> str:
        """Метод для получения перевода по ключу"""
        return LOCALIZATION[self.current_language].get(key, key)


    def on_resize(self, width, height):
            """Вызывается при изменении размера окна"""
            super().on_resize(width, height)
            
            # Обновляем глобальные переменные с размерами
            global SCREEN_WIDTH, SCREEN_HEIGHT
            SCREEN_WIDTH = width
            SCREEN_HEIGHT = height
            
            # Обновляем позиции элементов интерфейса
            self.update_ui_positions()
            
            # Обновляем позиции карт, если игра активна
            if self.game_state:
                self.calculate_positions()
                for i, player in enumerate(self.game_state.players):
                    x, y, angle = self.player_positions[i]
                    self.position_cards(player.hand, x, y, angle, player.is_human)
    def update_ui_positions(self):
        """Обновляет позиции UI элементов при изменении размера окна"""
        if self.current_screen == "settings":
            self.buttons = [
                # Левая колонка
                Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                    self.tr("toggle_fullscreen"), lambda: self.toggle_fullscreen(), self),
                Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                    self.tr("sound_on_off"), lambda: self.sound_manager.toggle_sound(), self),
                Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT,
                    self.tr("switch_monitor"), lambda: self.switch_monitor(), self),
                Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                    self.tr("change_resolution"), lambda: self.change_resolution(), self),
                
                # Правая колонка
                Button(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                    "English", lambda: self.set_language("en"), self),
                Button(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT,
                    "Русский", lambda: self.set_language("ru"), self),
                
                # Кнопка "Назад"
                Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                    self.tr("back"), lambda: self.setup_main_menu(), self)
            ]
            
            # Обновляем позицию слайдера громкости
            self.volume_slider = {
                "x": SCREEN_WIDTH//2,
                "y": SCREEN_HEIGHT//2,
                "width": 300,
                "height": 20,
                "dragging": False,
                "min_x": SCREEN_WIDTH//2 - 150,
                "max_x": SCREEN_WIDTH//2 + 150,
                "knob_x": SCREEN_WIDTH//2 - 150 + 300 * self.master_volume
            }
    def get_screen_size(self):
        """Возвращает размеры экрана"""
        return self.monitors[self.current_monitor].width, self.monitors[self.current_monitor].height
    
    def switch_monitor(self):
        """Переключение на следующий монитор"""
        self.current_monitor = (self.current_monitor + 1) % len(self.monitors)
        monitor = self.monitors[self.current_monitor]
        
        # Обновляем имя монитора для отображения
        try:
            self.current_monitor_name = monitor.name if hasattr(monitor, 'name') else f"Monitor {self.current_monitor+1}"
        except:
            self.current_monitor_name = f"Monitor {self.current_monitor+1}"
        
        # Добавляем разрешение к имени
        self.current_monitor_name += f" ({monitor.width}x{monitor.height})"
        
        if self.fullscreen:
            self.toggle_fullscreen()  # Сначала выходим из полноэкранного режима
            self.toggle_fullscreen()  # Затем снова входим с новым монитором

    def apply_resolution(self, resolution):
        """Применяет выбранное разрешение"""
        if resolution == "Fullscreen":
            self.toggle_fullscreen()
        else:
            if self.fullscreen:
                self.toggle_fullscreen()  # Сначала выходим из полноэкранного режима
                
            width, height = map(int, resolution.split('x'))
            self.set_size(width, height)
            self.set_viewport(0, width, 0, height)
        
        self.resolution_dialog = None
        self.setup_settings()  # Обновляем экран настроек

    def change_resolution(self):
        """Показывает диалог выбора разрешения"""
        self.resolution_dialog = {
            "active": True,
            "selected": None
        }
        
        # Создаем кнопки для каждого разрешения
        self.resolution_buttons = []
        for i, res in enumerate(self.resolutions):
            btn = Button(
                SCREEN_WIDTH//2, 
                SCREEN_HEIGHT//2 + 100 - i * 40,  # Располагаем кнопки вертикально
                BUTTON_WIDTH, 
                30,  # Высота кнопки
                res,
                lambda r=res: self.apply_resolution(r),
                self  # Передаем родителя (GameUI)
            )
            self.resolution_buttons.append(btn)

    def toggle_fullscreen(self):
        # Переключаем режим
        self.set_fullscreen(not self.fullscreen)
        
        if self.fullscreen:
            # В полноэкранном режиме просто переключаемся без изменения размеров
            monitor = self.monitors[self.current_monitor]
            self.set_location(monitor.x, monitor.y)
        else:
            # В оконном режиме возвращаем стандартные размеры
            self.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        
        # Принудительно обновляем отображение
        self.on_draw()

    def draw_text_with_font(self, text, x, y, color, font_size=20, 
                       anchor_x="center", anchor_y="center", 
                       font_name=None):
        """Универсальный метод отрисовки текста"""
        # Если явно указан шрифт или выбран Minecraft
        if (font_name == "minecraft" or 
            (self.current_font == "minecraft" and font_name is None)):
            if self.minecraft_font_name:
                arcade.draw_text(text, x, y, color, font_size,
                                font_name=self.minecraft_font_name,
                                anchor_x=anchor_x, anchor_y=anchor_y)
            else:
                arcade.draw_text(text, x, y, color, font_size,
                            anchor_x=anchor_x, anchor_y=anchor_y)
        else:
            arcade.draw_text(text, x, y, color, font_size,
                            anchor_x=anchor_x, anchor_y=anchor_y)

    def load_fonts(self):
        """Загрузка шрифтов с явным указанием для Arcade"""
        try:
            # Путь к шрифту
            font_path = os.path.join("fonts", "minecraft.ttf")
            
            if not os.path.exists(font_path):
                print(f"Файл шрифта не найден: {os.path.abspath(font_path)}")
                self.minecraft_font = None
                return
                
            try:
                # Явно регистрируем шрифт для Arcade
                arcade.text.load_font(font_path)
                
                # Сохраняем имя шрифта (может отличаться от имени файла)
                self.minecraft_font_name = "Minecraft"  # Замените на реальное имя из файла .ttf
                
                print(f"Шрифт {self.minecraft_font_name} успешно загружен")
                self.current_font = "minecraft"  # Устанавливаем Minecraft как шрифт по умолчанию
            except Exception as e:
                print(f"Ошибка загрузки шрифта: {e}")
                self.minecraft_font_name = None
        except Exception as e:
            print(f"Общая ошибка: {e}")
            self.minecraft_font_name = None

    def toggle_font(self):
            """Переключение между шрифтами"""
            if self.minecraft_font:
                self.current_font = "minecraft" if self.current_font == "default" else "default"
                print(f"Текущий шрифт: {self.current_font}")

    

    def setup_main_menu(self):
        self.current_screen = "main_menu"
        self.buttons = [
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("play_vs_bot"), lambda: self.setup_single_player_game(), self),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, BUTTON_WIDTH, BUTTON_HEIGHT, 
                self.tr("create_lobby"), lambda: self.setup_create_lobby(), self),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT, 
                self.tr("join_lobby"), lambda: self.show_lobby_list(), self),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, BUTTON_WIDTH, BUTTON_HEIGHT, 
                self.tr("settings"), lambda: self.setup_settings(), self),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, BUTTON_WIDTH, BUTTON_HEIGHT, 
                self.tr("exit"), lambda: self.close(), self)
        ]
    def setup_settings(self):
        self.current_screen = "settings"
        # Получаем информацию о мониторах
        monitor_info = []
        for i, monitor in enumerate(self.monitors):
            name = f"Monitor {i+1}"  # Базовое имя, если не удалось получить настоящее
            try:
                # Пытаемся получить более точное имя монитора
                name = monitor.name if hasattr(monitor, 'name') else f"Monitor {i+1}"
            except:
                pass
            
            resolution = f"{monitor.width}x{monitor.height}"
            monitor_info.append(f"{name} ({resolution})")
        
        self.current_monitor_name = monitor_info[self.current_monitor]
        
        # Варианты разрешений
        self.resolutions = [
            "640x480",
            "800x600",
            "1024x768",
            "1280x720",
            "1366x768",
            "1600x900",
            "1920x1080",
            "Fullscreen"
        ]
        
        # Новое расположение кнопок - две колонки
        self.buttons = [
            # Левая колонка
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("toggle_fullscreen"), lambda: self.toggle_fullscreen(), self),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("sound_on_off"), lambda: self.sound_manager.toggle_sound(), self),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("switch_monitor"), lambda: self.switch_monitor(), self),
            Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("change_resolution"), lambda: self.change_resolution(), self),
            
            # Правая колонка
            Button(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 + 100, BUTTON_WIDTH, BUTTON_HEIGHT,
                "English", lambda: self.set_language("en"), self),
            Button(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT,
                "Русский", lambda: self.set_language("ru"), self),
            
            # Кнопка "Назад" внизу по центру
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                self.tr("back"), lambda: self.setup_main_menu(), self)
        ]
        
    def draw_settings(self):
        # Фон
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_manager.background)
        
        # Если открыт диалог выбора разрешения - рисуем его первым
        if self.resolution_dialog and self.resolution_dialog["active"]:
            # Затемнение фона
            arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))
            
            # Окно выбора разрешения
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                400, 400,
                arcade.color.DARK_SLATE_GRAY
            )
            arcade.draw_rectangle_outline(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                400, 400,
                arcade.color.GOLD, 3
            )
            
            # Заголовок
            arcade.draw_text(
                "Выберите разрешение",
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160,
                arcade.color.WHITE, 24,
                anchor_x="center", anchor_y="center"
            )
            
            # Кнопки с разрешениями
            for button in self.resolution_buttons:
                button.draw()
                
            # Выходим, чтобы не рисовать остальные элементы поверх диалога
            return
        
        # Остальной код отрисовки настроек (только если диалог не активен)
        # Заголовок
        arcade.draw_text("SETTINGS", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100,
                        arcade.color.GOLD, 40, anchor_x="center", font_name=self.minecraft_font_name)
        
        # Панель настроек
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 600, 400, (0, 0, 0, 180))
        
        # Информация о текущем мониторе
        arcade.draw_text(f"Current Monitor: {self.current_monitor_name}", 
                        SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150,
                        arcade.color.WHITE, 20, anchor_x="center")
        
        # Информация о текущем разрешении
        current_res = f"{self.width}x{self.height}" if not self.fullscreen else "Fullscreen"
        arcade.draw_text(f"Current Resolution: {current_res}", 
                        SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120,
                        arcade.color.WHITE, 20, anchor_x="center")
        
        # Кнопки
        for button in self.buttons:
            button.draw()


    def handle_volume_slider(self, x, y):
        if self.current_screen == "settings":
            # Ограничиваем положение ползунка
            new_x = max(self.volume_slider["min_x"], min(x, self.volume_slider["max_x"]))
            self.volume_slider["knob_x"] = new_x
            
            # Вычисляем новую громкость (от 0 до 1)
            self.master_volume = (new_x - self.volume_slider["min_x"]) / self.volume_slider["width"]
            
            # Применяем громкость ко всем звукам через SoundManager
            self.sound_manager.set_volume(self.master_volume)


    def setup_single_player_game(self):
        self.current_screen = "game"
        self.buttons.clear()
        self.message = ""
        self.game_state = GameState()
        
        # Один игрок — человек, другой — бот
        players_info = [
            {"name": self.player_name, "is_you": True},
            {"name": "Bot", "is_you": False}
        ]
        trump_suit = random.choice(SUITS)
        self.game_state.init_game(players_info, trump_suit, 0)
        self.calculate_positions()

    def setup_load_background(self):
        """Настройка экрана загрузки фона"""
        self.current_screen = "load_background"
        self.buttons = [
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT, 
                  "Enter Path", lambda: self.set_active_input("background")),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, BUTTON_WIDTH, BUTTON_HEIGHT, 
                  "Load", lambda: self.load_background()),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, BUTTON_WIDTH, BUTTON_HEIGHT, 
                  "Back", lambda: self.setup_main_menu())
        ]
        self.input_text = ""
        self.active_input = None
        
    def set_active_input(self, input_type):
        self.active_input = input_type
        self.input_text = ""
        
    def load_background(self):
        if self.input_text:
            if self.background_manager.load_custom_background(self.input_text):
                self.message = "Фон успешно загружен!"
            else:
                self.message = "Ошибка загрузки фона"
        else:
            self.message = "Введите путь к файлу фона"
            
    def setup_create_lobby(self):
        if not self.network.connected:
            # Попробуем переподключиться
            if not self.network.connect(SERVER_HOST, SERVER_PORT):
                self.message = "Не удалось подключиться к серверу!"
                return
                
        self.current_screen = "create_lobby"
        self.input_text = ""
        self.active_input = "lobby_name"
        
        self.buttons = [
            Button(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, 
                BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Создать", 
                lambda: self.create_lobby()
            ),
            Button(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, 
                BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Назад", 
                lambda: self.setup_main_menu()
            )
        ]
        
    def show_lobby_list(self):
        self.current_screen = "lobby_list"
        self.buttons = [
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200, BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Refresh", lambda: self.network.send_message({"action": "list_lobbies"})),
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 260, BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Back", lambda: self.setup_main_menu())
        ]
        # Немедленно запрашиваем список
        self.network.send_message({"action": "list_lobbies"})
            
    def setup_lobby(self, lobby_info):
        self.current_screen = "lobby"
        self.current_lobby = lobby_info
        self.buttons = []
        
        # Проверяем, является ли текущий игрок создателем лобби
        if lobby_info.get("creator") == self.player_name:
            self.buttons.append(
                Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, BUTTON_WIDTH, BUTTON_HEIGHT, 
                    "Start Game", lambda: self.start_game())
            )
        
        self.buttons.append(
            Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 180, BUTTON_WIDTH, BUTTON_HEIGHT, 
                "Leave Lobby", lambda: self.leave_lobby())
        )
        
    def setup_game(self, game_info):
        self.current_screen = "game"
        self.game_state = GameState()
        
        # ФИКС: Правильно определяем индекс игрока
        your_index = next((i for i, p in enumerate(game_info["players"]) if p.get("is_you")), 0)
        
        self.game_state.init_game(game_info["players"], game_info["trump_suit"], your_index)
        self.calculate_positions()
        
    def create_lobby(self):
        print(f"Попытка создать лобби. Подключение: {self.network.connected}, текст: {self.input_text}")
        if not self.input_text:
            self.message = "Введите название лобби"
            return
            
        if not self.network.connected:
            self.message = "Нет подключения к серверу"
            return
            
        self.message = "Создание лобби..."
        lobby_name = self.input_text[:20]
        
        # Используем уникальное имя игрока
        print(f"Мое имя: {self.player_name}")
        print(f"Отправка запроса на создание лобби: {lobby_name}")
        success = self.network.send_message({
            "action": "create_lobby",
            "name": lobby_name,
            "password": None,
            "player_name": self.player_name  # Добавляем имя игрока
        })
        
    def join_lobby(self, lobby_id):
        self.network.send_message({
            "action": "join_lobby",
            "lobby_id": lobby_id,
            "password": None,  # Можно добавить поле для пароля
            "player_name": self.player_name
        })
        
    def leave_lobby(self):
        self.network.send_message({"action": "leave_lobby"})
        self.current_lobby = None
        self.setup_main_menu()
        
    def start_game(self):
        # Для одиночной игры показываем подтверждение
        if len(self.current_lobby["players"]) < MAX_PLAYERS_PER_LOBBY:
            self.show_confirmation_dialog(
                "Начать игру без полного лобби?",
                lambda: self.send_start_game_request()
            )
        else:
            self.send_start_game_request()

    def send_start_game_request(self):
        self.network.send_message({"action": "start_game"})

    def show_confirmation_dialog(self, message, on_confirm):
        self.confirmation_dialog = {
            "message": message,
            "on_confirm": on_confirm,
            "active": True
        }
        self.buttons = [
            Button(SCREEN_WIDTH//2 - 110, 150, 200, 50, "Да", lambda: self.handle_confirmation(True)),
            Button(SCREEN_WIDTH//2 + 110, 150, 200, 50, "Нет", lambda: self.handle_confirmation(False))
        ]

    def handle_confirmation(self, confirmed):
        if confirmed and self.confirmation_dialog["active"]:
            self.confirmation_dialog["on_confirm"]()
        self.confirmation_dialog = None
        self.setup_lobby(self.current_lobby)  # Восстанавливаем обычные кнопки лобби

    def calculate_positions(self):
        if not self.game_state:
            return
            
        self.player_positions = []
        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        
        # Позиции игроков
        for i, player in enumerate(self.game_state.players):
            if player.is_human:
                # Для игрока-человека - снизу по центру
                x = center_x
                y = SCREEN_HEIGHT * 0.15
                angle = 0
            else:
                # Для бота - сверху по центру
                x = center_x
                y = SCREEN_HEIGHT * 0.85
                angle = math.pi
            self.player_positions.append((x, y, angle))
            
        # Позиция колоды (слева посередине)
        self.deck_position = (SCREEN_WIDTH * 0.1, center_y, 0)
            
    def position_cards(self, cards: List[Card], pos_x: float, pos_y: float, angle: float, is_human: bool):
        """Позиционирование карт с учетом типа игрока"""
        if not cards:
            return
                
        spacing = CARD_WIDTH * 0.7
        total_width = len(cards) * spacing
        start_x = pos_x - total_width / 2
        
        for i, card in enumerate(cards):
            card.target_x = start_x + i * spacing
            # Для карт игрока располагаем их ниже
            card.target_y = pos_y if not is_human else pos_y * 0.9
            card.angle = angle
            card.face_up = is_human

    def on_draw(self):
        arcade.start_render()
        
        # Фон - теперь используем BackgroundManager
        self.background_manager.draw()
                
        if self.current_screen == "main_menu":
            self.draw_main_menu()
        elif self.current_screen == "load_background":
            self.draw_load_background()
        elif self.current_screen == "create_lobby":
            self.draw_create_lobby()
        elif self.current_screen == "lobby_list":
            self.draw_lobby_list()
        elif self.current_screen == "lobby":
            self.draw_lobby()
        elif self.current_screen == "game":
            self.draw_game()
        elif self.current_screen == "settings":
            self.draw_settings()
            
        # Кнопки
        for button in self.buttons:
            button.draw()
            
        # Диалог подтверждения
        if self.confirmation_dialog and self.confirmation_dialog["active"]:
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                600, 200,
                arcade.color.DARK_SLATE_GRAY
            )
            arcade.draw_text(
                self.confirmation_dialog["message"],
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50,
                arcade.color.WHITE, 24,
                width=500,
                align="center",
                anchor_x="center",
                anchor_y="center"
            )
            
        # Сообщение
        if self.message:
            arcade.draw_text(
                self.message, 
                SCREEN_WIDTH//2, 30,
                arcade.color.WHITE, 20,
                anchor_x="center"
            )
        if self.winner_window and self.winner_window["active"]:
            self.draw_winner_window()
        
    def draw_main_menu(self):
        # Фоновый градиент
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_manager.background)
        
        # Заголовок с тенью
        arcade.draw_text("DURAK ONLINE", SCREEN_WIDTH//2 + 3, SCREEN_HEIGHT - 103,
                        arcade.color.BLACK, 50, anchor_x="center", font_name=self.minecraft_font_name)
        arcade.draw_text("DURAK ONLINE", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100,
                        arcade.color.GOLD, 50, anchor_x="center", font_name=self.minecraft_font_name)
        
        # Версия игры
        arcade.draw_text("v1.0", SCREEN_WIDTH - 50, 20, arcade.color.WHITE, 12)
        
        # Имя игрока
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT - 160, 300, 30, (0, 0, 0, 150))
        arcade.draw_text(f"Player: {self.player_name}", SCREEN_WIDTH//2, SCREEN_HEIGHT - 165,
                        arcade.color.WHITE, 20, anchor_x="center")
        
        # Кнопки с эффектом стекла
        for button in self.buttons:
            color = (200, 200, 200, 150) if button.hovered else (100, 100, 100, 150)
            arcade.draw_rectangle_filled(button.x, button.y, button.width, button.height, color)
            arcade.draw_rectangle_outline(button.x, button.y, button.width, button.height, arcade.color.WHITE, 2)
            
            text_color = arcade.color.GOLD if button.hovered else arcade.color.WHITE
            arcade.draw_text(button.text, button.x, button.y, text_color, 20,
                            anchor_x="center", anchor_y="center", font_name=self.minecraft_font_name)
        
    def draw_load_background(self):
        arcade.draw_text("Load Custom Background", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, 
                        arcade.color.WHITE, 40, anchor_x="center")
        
        arcade.draw_text("Enter path to background image:", 
                         SCREEN_WIDTH//2, SCREEN_HEIGHT - 120, 
                         arcade.color.WHITE, 20, anchor_x="center")
        
        # Рисуем поле ввода
        color = arcade.color.LIGHT_BLUE if self.active_input else arcade.color.WHITE
        arcade.draw_rectangle_outline(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, 600, 40, color, 2)
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60, 600, 40, arcade.color.BLACK)
        
        # Отображаем текст с курсором, если поле активно
        text = self.input_text
        if self.active_input and int(time.time()) % 2 == 0:  # Мигающий курсор
            text += "|"
        arcade.draw_text(text, SCREEN_WIDTH//2 - 290, SCREEN_HEIGHT//2 - 70, 
                        arcade.color.WHITE, 20)
        
    def draw_create_lobby(self):
        arcade.draw_text("Create Lobby", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100, 
                        arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text("Lobby Name:", SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 20, 
                        arcade.color.WHITE, 20)
        
        # Рисуем поле ввода с индикатором активного состояния
        color = arcade.color.LIGHT_BLUE if self.active_input else arcade.color.WHITE
        arcade.draw_rectangle_outline(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 300, 40, color, 2)
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 300, 40, arcade.color.BLACK)
        
        # Отображаем текст с курсором, если поле активно
        text = self.input_text
        if self.active_input and int(time.time()) % 2 == 0:  # Мигающий курсор
            text += "|"
        arcade.draw_text(text, SCREEN_WIDTH//2 - 140, SCREEN_HEIGHT//2 - 10, 
                        arcade.color.WHITE, 20)
        
    def draw_lobby_list(self):
        arcade.draw_text("Available Lobbies", SCREEN_WIDTH//2, SCREEN_HEIGHT - 60, 
                        arcade.color.WHITE, 30, anchor_x="center")
        
        # Рисуем сообщение, если лобби нет
        if not self.lobbies:
            arcade.draw_text("No lobbies available", SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 
                            arcade.color.WHITE, 20, anchor_x="center")
        
        # Рисуем список лобби и кнопки
        self.lobby_buttons = []  # Очищаем старые кнопки
        for i, lobby in enumerate(self.lobbies):
            y_pos = SCREEN_HEIGHT - 120 - i * 60
            
            # Рисуем информацию о лобби
            arcade.draw_text(
                f"{lobby['name']} ({lobby['player_count']}/{lobby['max_players']})", 
                SCREEN_WIDTH//2 - 200, y_pos, 
                arcade.color.WHITE, 20
            )
            
            # Создаем и рисуем кнопку Join, если лобби не начато
            if not lobby["game_started"]:
                btn = Button(
                    SCREEN_WIDTH//2 + 200, y_pos, 
                    100, 30, 
                    "Join", 
                    lambda l=lobby: self.join_lobby(l["id"])
                )
                btn.draw()
                self.lobby_buttons.append(btn)
                
    def draw_lobby(self):
        if not self.current_lobby:
            return
            
        # Фон
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_manager.background)
        
        # Заголовок
        arcade.draw_text(f"LOBBY: {self.current_lobby['name']}", SCREEN_WIDTH//2, SCREEN_HEIGHT - 100,
                        arcade.color.GOLD, 30, anchor_x="center", font_name=self.minecraft_font_name)
        
        # Панель игроков
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 400, 300, (0, 0, 0, 180))
        arcade.draw_text("PLAYERS:", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120, arcade.color.WHITE, 24, anchor_x="center")
        
        for i, player in enumerate(self.current_lobby["players"]):
            color = arcade.color.GOLD if player == self.player_name else arcade.color.WHITE
            arcade.draw_text(f"• {player}", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80 - i * 40, color, 20, anchor_x="center")
        
        # Кнопки
        for button in self.buttons:
            color = (200, 200, 200, 200) if button.hovered else (100, 100, 100, 200)
            arcade.draw_rectangle_filled(button.x, button.y, button.width, button.height, color)
            arcade.draw_text(button.text, button.x, button.y, arcade.color.WHITE, 20,
                            anchor_x="center", anchor_y="center", font_name=self.minecraft_font_name)
            
    def draw_game(self):
        if not self.game_state:
            return
            
        # Фон игры
        self.background_manager.draw_game()
        
        # Затемнение фона под столом
        arcade.draw_lrtb_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 100))
        
        # Стол с текстурой дерева
        arcade.draw_circle_filled(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                        min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4, 
                        (139, 69, 19, 200))
        arcade.draw_circle_outline(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 
                        min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.4, 
                        (160, 82, 45), 5)
        
        # Информационная панель
        arcade.draw_rectangle_filled(SCREEN_WIDTH // 2, 30, SCREEN_WIDTH, 60, (0, 0, 0, 150))
        arcade.draw_text(f"Trump: {self.game_state.trump_suit} | Phase: {self.game_state.game_phase} | Cards left: {len(self.game_state.deck)}", 
                        SCREEN_WIDTH // 2, 30, arcade.color.WHITE, 18, anchor_x="center")
        
        # Карты игроков с анимацией
        for i, player in enumerate(self.game_state.players):
            x, y, angle = self.player_positions[i]
            self.position_cards(player.hand, x, y, angle, player.is_human)
            
            # Имя игрока
            name_color = arcade.color.GOLD if i == self.game_state.current_player_idx else arcade.color.WHITE
            arcade.draw_text(player.name + (" (You)" if player.is_human else ""), 
                            x, y - 120, name_color, 16, anchor_x="center")
            
            # Карты игрока
            for card in player.hand:
                card.draw()

        field_x = SCREEN_WIDTH // 2 - (len(self.game_state.field) * CARD_WIDTH * 0.4) // 2
        field_y = SCREEN_HEIGHT // 2

        # Карты на столе
        for i, card in enumerate(self.game_state.field):
            # Позиционируем карты горизонтально с небольшим смещением
            card.target_x = field_x + i * CARD_WIDTH * 0.4
            card.target_y = field_y
            card.angle = 0
            card.draw()
            
        # Кнопки действий с эффектом свечения
        if self.game_state.players[self.game_state.current_player_idx].is_human:
            arcade.draw_rectangle_filled(SCREEN_WIDTH - 100, 100, 150, 100, (100, 100, 100, 150))
            arcade.draw_rectangle_outline(SCREEN_WIDTH - 100, 100, 150, 100, arcade.color.WHITE, 2)
            
            play_color = arcade.color.GREEN if self.selected_card_idx >= 0 else arcade.color.GRAY
            arcade.draw_text("PLAY", SCREEN_WIDTH - 100, 70, play_color, 20, anchor_x="center")
            arcade.draw_text("PASS", SCREEN_WIDTH - 100, 130, arcade.color.RED, 20, anchor_x="center")

        if self.game_state.deck:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2,
                CARD_WIDTH, CARD_HEIGHT,
                arcade.load_texture("card/card_back.png")
            )
            arcade.draw_text(
                f"{len(self.game_state.deck)}", 
                SCREEN_WIDTH * 0.1, SCREEN_HEIGHT // 2 - CARD_HEIGHT//2 - 20,
                arcade.color.WHITE, 20, anchor_x="center"
            )
                
    def on_mouse_motion(self, x, y, dx, dy):
        # Обрабатываем основные кнопки
        for button in self.buttons:
            button.check_hover(x, y)
        
        # Обрабатываем кнопки лобби
        for button in self.lobby_buttons:
            button.check_hover(x, y)
        
        # Обрабатываем кнопки разрешения (если диалог активен)
        if self.current_screen == "settings" and self.resolution_dialog and self.resolution_dialog["active"]:
            for button in self.resolution_buttons:
                button.check_hover(x, y)
        
        if self.winner_window and self.winner_window["active"]:
            self.return_button_hovered = (
                abs(x - SCREEN_WIDTH//2) <= 100 and 
                abs(y - (SCREEN_HEIGHT//2 - 60)) <= 25
            )

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Воспроизводим звук нажатия
            self.sound_manager.play_sound("button_click")
            
            # Проверка нажатия на ползунок громкости
            if self.current_screen == "settings":
                if (abs(x - self.volume_slider["knob_x"])) < 20 and \
                abs(y - self.volume_slider["y"]) < 20:
                    self.volume_slider["dragging"] = True
                    return
            
            # Обработка кликов по кнопкам разрешения (если диалог активен)
            if self.current_screen == "settings" and self.resolution_dialog and self.resolution_dialog["active"]:
                for btn in self.resolution_buttons:
                    if btn.check_hover(x, y) and btn.action:
                        btn.action()
                        return

            if (self.winner_window and self.winner_window["active"] and 
                abs(x - SCREEN_WIDTH//2) <= 100 and 
                abs(y - (SCREEN_HEIGHT//2 - 60)) <= 25):
                self.winner_window["active"] = False
                self.winner_window = None
                self.game_state = None
                self.setup_main_menu()
                return
            # Если мы в игровом экране, обрабатываем клики игры
            if self.current_screen == "game":
                self.handle_game_click(x, y)
                return
                
            # Проверяем основные кнопки
            for btn in self.buttons:
                if btn.check_hover(x, y) and btn.action:
                    btn.action()
                    return
                    
            # Проверяем кнопки лобби
            for btn in self.lobby_buttons:
                if btn.check_hover(x, y) and btn.action:
                    btn.action()
                    return
                

                
    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.current_screen == "settings":
                self.volume_slider["dragging"] = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            if self.current_screen == "settings" and self.volume_slider["dragging"]:
                self.handle_volume_slider(x, y)



    def handle_game_click(self, x, y):
        if self.is_animating:
            self.message = self.tr("wait_turn_end")
            return
        
        if not self.game_state:
            return
            
        current_player = self.game_state.players[self.game_state.current_player_idx]
        if current_player.is_human:
            for i, card in enumerate(current_player.hand):
                if (card.x - CARD_WIDTH/2 < x < card.x + CARD_WIDTH/2 and 
                    card.y - CARD_HEIGHT/2 < y < card.y + CARD_HEIGHT/2):
                    self.selected_card_idx = i
                    # Сбрасываем выделение всех карт
                    for c in current_player.hand:
                        c.selected = False
                    card.selected = True
                    return
            
        # Кнопка паса/игры
        if (SCREEN_WIDTH - 175 < x < SCREEN_WIDTH - 25 and 
            50 < y < 150):
            if y > 100:  # Pass
                if self.game_state.pass_move(self.game_state.current_player_idx):
                    self.message = self.tr("you_take_cards")
                    card = None
                    if self.selected_card_idx >= 0:
                        card = current_player.hand[self.selected_card_idx]
                    if self.game_state.players[0].is_human:  # Если это игрок
                        # Воспроизводим звук карты
                        self.sound_manager.play_sound("card_place")
                    self.selected_card_idx = -1
                else:
                    self.message = self.tr("invalid_move")
                self.selected_card_idx = -1
            else:  # Play
                if self.selected_card_idx >= 0:
                    card = current_player.hand[self.selected_card_idx]
                    # Проверяем валидность хода перед броском
                    if ((self.game_state.game_phase == "attack" and not self.game_state.is_valid_attack(card)) or
                        (self.game_state.game_phase == "defense" and not self.game_state.is_valid_defense(card)) or
                        (self.game_state.game_phase == "throw" and not self.game_state.is_valid_throw(card))):
                        self.message = self.tr("invalid_move")
                        return
                    
                    # Изменяем точку назначения анимации - теперь карта летит в центр стола (нижняя часть)
                    center_x = SCREEN_WIDTH // 2
                    center_y = SCREEN_HEIGHT * 0.35  # Ниже центра, ближе к игроку
                    
                    # Запускаем анимацию
                    card.start_animation('throw', (card.x, card.y))
                    card.target_x = center_x  # Устанавливаем конечную позицию
                    card.target_y = center_y
                    
                    if self.game_state.make_move(self.game_state.current_player_idx, self.selected_card_idx):
                        # Воспроизводим звук карты
                        self.sound_manager.play_sound("card_place")
                        self.message = self.tr("card_played")
                    else:
                        self.message = self.tr("invalid_move")
                    self.selected_card_idx = -1
                
    def on_key_press(self, key, modifiers):
        if self.active_input:
            if key == arcade.key.BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif key == arcade.key.ENTER or key == arcade.key.ESCAPE:
                self.active_input = None
            elif key == arcade.key.SPACE:
                self.input_text += " "

    def on_text(self, text):
        if self.active_input:
            self.input_text += text

                
    def on_update(self, delta_time):
        # Обновление анимаций
        if self.game_state:
            for player in self.game_state.players:
                for card in player.hand:
                    card.update()
            for card in self.game_state.field:
                card.update()
                
            # Проверка времени хода
            if time.time() - self.game_state.last_move_time > self.game_state.move_timeout:
                self.message = "Player timeout - passing turn"
                self.game_state.pass_move(self.game_state.current_player_idx)
            
            if self.game_state and not self.game_state.players[self.game_state.current_player_idx].is_human:
                self.make_bot_move()

            # Проверка конца игры
            if self.game_state.check_game_over():
                # Воспроизводим звук выигрыша
                self.sound_manager.play_sound("win")
                self.message = f"{self.game_state.players[self.game_state.winner].name} wins!"

        if self.game_state and self.game_state.check_game_over():
            if not self.winner_window:  # Показываем окно только если оно еще не показано
                winner_name = self.game_state.players[self.game_state.winner].name
                self.winner_window = {
                    "winner": winner_name,
                    "active": True
                }
                self.sound_manager.play_sound("win")
        # Обработка сетевых сообщений
        while self.network.message_queue:
            message = self.network.message_queue.pop(0)
            self.process_network_message(message)
    
    def draw_winner_window(self):
        if not self.winner_window or not self.winner_window["active"]:
            return
            
        # Затемнение фона
        arcade.draw_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 180))
        
        # Окно победы
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
            500, 300,
            arcade.color.DARK_SLATE_GRAY
        )
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
            500, 300,
            arcade.color.GOLD, 3
        )
        
        # Текст с победителем
        arcade.draw_text(
            "ПОБЕДА!",
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100,
            arcade.color.GOLD, 40,
            anchor_x="center", anchor_y="center",
            font_name=self.minecraft_font_name
        )
        arcade.draw_text(
            f"Победитель: {self.winner_window['winner']}",
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
            font_name=self.minecraft_font_name
        )
        
        # Кнопка "Вернуться"
        color = (200, 200, 200, 200) if self.return_button_hovered else (100, 100, 100, 200)
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60,
            200, 50,
            color
        )
        arcade.draw_text(
            "Вернуться",
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60,
            arcade.color.WHITE, 24,
            anchor_x="center", anchor_y="center",
            font_name=self.minecraft_font_name
        )

    def make_bot_move(self):
        bot = self.game_state.players[self.game_state.current_player_idx]
        
        if self.game_state.game_phase == "attack":
            for i, card in enumerate(bot.hand):
                if self.game_state.is_valid_attack(card):
                    card.face_up = True  # Переворачиваем карту при броске
                    self.game_state.make_move(bot.idx, i)
                    return
                    
        elif self.game_state.game_phase == "defense":
            attacking_card = self.game_state.field[-1]
            valid_defense_cards = []
            for i, card in enumerate(bot.hand):
                if self.game_state.can_beat(attacking_card, card):
                    valid_defense_cards.append((i, card))
            
            if valid_defense_cards:
                # Сначала пробуем отбиться картой той же масти
                same_suit = [c for c in valid_defense_cards if c[1].suit == attacking_card.suit]
                if same_suit:
                    same_suit.sort(key=lambda x: RANK_VALUES[x[1].rank])  # Выбираем минимальную карту той же масти
                    chosen_card = same_suit[0]
                else:
                    # Иначе используем минимальный козырь
                    valid_defense_cards.sort(key=lambda x: (x[1].suit != self.game_state.trump_suit, RANK_VALUES[x[1].rank]))
                    chosen_card = valid_defense_cards[0]
                card.face_up = True
                self.game_state.make_move(bot.idx, chosen_card[0])
                return
            else:
                # Если не можем отбиться - забираем карты
                self.game_state.pass_move(bot.idx)
            
        elif self.game_state.game_phase == "throw":
            valid_throw_cards = []
            for i, card in enumerate(bot.hand):
                if self.game_state.is_valid_throw(card):
                    valid_throw_cards.append((i, card))
            
            if valid_throw_cards:
                # Подкидываем карты с наименьшим достоинством
                valid_throw_cards.sort(key=lambda x: RANK_VALUES[x[1].rank])
                chosen_card = valid_throw_cards[0]
                card.face_up = True
                self.game_state.make_move(bot.idx, chosen_card[0])
                return
            else:
                # Если нечего подкинуть - завершаем кон
                self.game_state.pass_move(bot.idx)


    def process_network_message(self, message: Dict):
        print("Получено сообщение от сервера:", message)
        
        if message.get("status") == "error":
            error_msg = message.get("message", "Неизвестная ошибка")
            print(f"Ошибка сервера: {error_msg}")
            self.message = error_msg
            return
            
        action = message.get("action")
        
        if action == "lobbies_list":
            self.lobbies = message.get("lobbies", [])
            print(f"Обновлен список лобби: {len(self.lobbies)} доступно")
        # Принудительно обновляем экран
            if self.current_screen == "lobby_list":
                arcade.schedule(lambda delta_time: None, 0)  # Триггер обновления экрана
            
        elif action == "lobby_update":
            self.current_lobby = message.get("lobby")
            if self.current_lobby:
                print(f"Обновление лобби: {self.current_lobby['name']}")
                self.setup_lobby(self.current_lobby)
                
        elif action == "game_start":
            print("Игра начинается!")
            if message.get("forced_start"):
                print("Игра начата принудительно создателем лобби")
            self.setup_game(message)

        elif action == "left_lobby":
            self.setup_main_menu()

            
        elif action == "game_state":
            print("Обновление состояния игры")
            if self.game_state:
                self.game_state.field = []
                for card_info in message.get('field', []):
                    # Создаем карту и устанавливаем face_up=True
                    card = Card(card_info['suit'], card_info['rank'])
                    card.face_up = True  # Важное исправление!
                    self.game_state.field.append(card)
                self.game_state.current_player_idx = message.get('current_player_idx', 0)
                self.game_state.game_phase = message.get('game_phase', 'attack')
            
        elif action == "success":
            success_msg = message.get("message", "")
            print(f"Успешная операция: {success_msg}")
            self.message = success_msg

        elif action == "game_action":
            # Обработка ходов других игроков
            player_idx = message.get("player_idx")
            action_type = message.get("type")
            card_key = message.get("card")
            
            if action_type == "play" and card_key:
                # ФИКС: Устанавливаем видимость карты
                rank, suit = card_key.split("_")  # Разделяем по подчеркиванию
                card = Card(suit, rank)
                card.face_up = True  # ВАЖНО: Делаем карту видимой
                card.x = self.player_positions[player_idx][0]
                card.y = self.player_positions[player_idx][1]
                card.start_animation('throw', (card.x, card.y))
                self.game_state.field.append(card)

def main():
    window = GameUI()
    arcade.run()

if __name__ == "__main__":
    main()
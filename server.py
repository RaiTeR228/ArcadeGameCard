import socket
import threading
import json
import random
from typing import Dict, List, Optional
import time

# Настройки сервера
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5555
BUFFER_SIZE = 4096
MAX_LOBBIES = 10
MAX_PLAYERS_PER_LOBBY = 2

class Lobby:
    def __init__(self, lobby_id: str, name: str, creator: 'ClientHandler'):
        self.id = lobby_id
        self.name = name
        self.players: List['ClientHandler'] = [creator]
        self.creator = creator
        self.game_started = False
        self.max_players = MAX_PLAYERS_PER_LOBBY
        self.password = None
        
    def add_player(self, player: 'ClientHandler') -> bool:
        if len(self.players) < self.max_players and not self.game_started:
            self.players.append(player)
            return True
        return False
        
    def remove_player(self, player: 'ClientHandler'):
        if player in self.players:
            self.players.remove(player)
            if not self.players and self in server.lobbies:
                server.remove_lobby(self)
                
    def get_info(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "players": [p.player_name for p in self.players],
            "player_count": len(self.players),
            "max_players": self.max_players,
            "game_started": self.game_started,
            "has_password": self.password is not None,
            "creator": self.creator.player_name if self.creator else None  # Добавляем создателя
        }

class ClientHandler(threading.Thread):
    def __init__(self, conn, addr, server):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.server = server
        self.player_name = f"Player{addr[1]}"
        self.lobby: Optional[Lobby] = None
        self.running = True
        
    def run(self):
        try:
            while self.running:
                data = self.conn.recv(BUFFER_SIZE)
                if not data:
                    break
                    
                try:
                    message = json.loads(data.decode())
                    self.handle_message(message)
                except json.JSONDecodeError:
                    self.send_error("Invalid JSON format")
                    
        except ConnectionError:
            pass
        finally:
            self.disconnect()
            
    def handle_message(self, message: Dict):
        if not isinstance(message, dict) or "action" not in message:
            self.send_error("Invalid message format")
            return
            
        action = message["action"]
        
        if action == "set_name":
            self.set_name(message.get("name"))
        elif action == "create_lobby":
            self.create_lobby(message.get("name"), message.get("password"))
        elif action == "join_lobby":
            self.join_lobby(message.get("lobby_id"), message.get("password"))
        elif action == "leave_lobby":
            self.leave_lobby()
        elif action == "start_game":
            self.start_game()
        elif action == "list_lobbies":
            self.list_lobbies()
        elif action == "game_action":
            self.handle_game_action(message)
        else:
            self.send_error(f"Unknown action: {action}")
            
    def set_name(self, name: str):
        if name and isinstance(name, str) and 2 <= len(name) <= 20:
            self.player_name = name
            self.send_success("Name updated")
        else:
            self.send_error("Invalid name (2-20 characters)")
            
    def create_lobby(self, name: str, password: str = None):
        if self.lobby:
            self.send_error("You are already in a lobby")
            return
            
        if not name or len(name) > 20:
            self.send_error("Lobby name must be 1-20 characters")
            return
            
        lobby_id = f"lobby{random.randint(1000, 9999)}"
        while lobby_id in [l.id for l in self.server.lobbies]:
            lobby_id = f"lobby{random.randint(1000, 9999)}"
            
        self.lobby = Lobby(lobby_id, name, self)
        if password:
            self.lobby.password = password
            
        self.server.lobbies.append(self.lobby)
        self.send_success("Lobby created", {
            "lobby": self.lobby.get_info(),
            "creator": self.player_name  # Добавляем информацию о создателе
        })
        self.broadcast_lobby_update()
        
    def join_lobby(self, lobby_id: str, password: str = None):
        if self.lobby:
            self.send_error("You are already in a lobby")
            return
            
        lobby = next((l for l in self.server.lobbies if l.id == lobby_id), None)
        if not lobby:
            self.send_error("Lobby not found")
            return
            
        if lobby.password and lobby.password != password:
            self.send_error("Incorrect password")
            return
            
        if lobby.game_started:
            self.send_error("Game already started")
            return
            
        if len(lobby.players) >= lobby.max_players:
            self.send_error("Lobby is full")
            return
            
        if lobby.add_player(self):
            self.lobby = lobby
            self.send_success("Joined lobby", {"lobby": lobby.get_info()})
            self.broadcast_lobby_update()
            
            # Автоматически начинаем игру при заполнении лобби
            if len(lobby.players) == lobby.max_players:
                lobby.creator.start_game()
        else:
            self.send_error("Could not join lobby")
            
    def leave_lobby(self):
        if not self.lobby:
            self.send_error("Not in a lobby")
            return
            
        was_creator = self.lobby.creator == self
        self.lobby.remove_player(self)
        self.lobby = None
        
        self.send_success("Left lobby")
        if not was_creator:  # чтобы избежать двойной рассылки при удалении лобби
            self.broadcast_lobby_update()
            
    def start_game(self):
        if not self.lobby:
            self.send_error("Not in a lobby")
            return
            
        if self.lobby.creator != self:
            self.send_error("Only lobby creator can start the game")
            return
            
        # Убираем проверку на минимальное количество игроков
        self.lobby.game_started = True
        self.broadcast_lobby_update()
        
        # Инициализация игры
        for player in self.lobby.players:
            game_init = {
                "action": "game_start",
                "players": [{
                    "id": i,
                    "name": p.player_name,
                    "is_you": p == player  # ФИКС: Только для текущего игрока
                } for i, p in enumerate(self.lobby.players)],
                "trump_suit": random.choice(["♠", "♥", "♦", "♣"]),
                "forced_start": len(self.lobby.players) < self.lobby.max_players
            }
            player.send_message(game_init)
        
        for i, player in enumerate(self.lobby.players):
            player.send_message(game_init)
                
    def handle_game_action(self, message: Dict):
        if not self.lobby or not self.lobby.game_started:
            self.send_error("Game not started")
            return
            
        # Пересылаем действие всем игрокам в лобби
        for player in self.lobby.players:
            if player != self:  # Отправителю не нужно отправлять его же действие
                player.send_message(message)
                
    def list_lobbies(self):
        try:
            # Получаем актуальный список всех лобби (не только текущего клиента)
            all_lobbies = self.server.lobbies
            
            # Формируем информацию о лобби
            lobbies_info = []
            for lobby in all_lobbies:
                # Включаем лобби, даже если игра началась (но помечаем это)
                lobby_info = lobby.get_info()
                
                # Добавляем дополнительную информацию
                lobby_info.update({
                    "can_join": not lobby.game_started and len(lobby.players) < lobby.max_players,
                    "is_yours": self in lobby.players
                })
                
                lobbies_info.append(lobby_info)
            
            # Отправляем полный список
            self.send_success("Lobbies list", {
                "action": "lobbies_list",  # Явно указываем действие
                "lobbies": lobbies_info
            })
            
            print(f"Sent lobbies list to {self.player_name}: {len(lobbies_info)} lobbies")  # Логирование
        except Exception as e:
            print(f"Error in list_lobbies: {str(e)}")
            self.send_error("Failed to get lobbies list")
        
    def broadcast_lobby_update(self):
        if not self.lobby:
            return
            
        lobby_info = self.lobby.get_info()
        for player in self.lobby.players:
            player.send_message({
                "action": "lobby_update",
                "lobby": lobby_info
            })
            
    def send_message(self, message: Dict):
        try:
            self.conn.sendall(json.dumps(message).encode())
        except ConnectionError:
            self.disconnect()
            
    def send_success(self, message: str, data: Dict = None):
        response = {"status": "success", "message": message}
        if data:
            response.update(data)
        self.send_message(response)
        
    def send_error(self, message: str):
        self.send_message({"status": "error", "message": message})
        
    def disconnect(self):
        if self.running:
            self.running = False
            if self.lobby:
                self.leave_lobby()
            self.conn.close()
            self.server.remove_client(self)

class DurakServer:
    def __init__(self):
        self.clients: List[ClientHandler] = []
        self.lobbies: List[Lobby] = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        self.server_socket.bind((SERVER_HOST, SERVER_PORT))
        self.server_socket.listen(5)
        print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")
        
        try:
            while True:
                conn, addr = self.server_socket.accept()
                print(f"New connection from {addr}")
                client = ClientHandler(conn, addr, self)
                self.clients.append(client)
                client.start()
        finally:
            self.stop()
            
    def remove_client(self, client: ClientHandler):
        if client in self.clients:
            self.clients.remove(client)
            
    def remove_lobby(self, lobby: Lobby):
        if lobby in self.lobbies:
            self.lobbies.remove(lobby)
            
    def stop(self):
        print("Shutting down server...")
        for client in self.clients[:]:
            client.disconnect()
        self.server_socket.close()

if __name__ == "__main__":
    server = DurakServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
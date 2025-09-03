import socket
import json

def main():
    socket_path = "/tmp/weather_service.sock"
    
    print(f"Попытка подключения к сокету: {socket_path}")
    
    try:
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(socket_path)
        print("Успешно подключено.")
        
        data = b""
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data += chunk
            
        if data:
            weather_data = json.loads(data.decode('utf-8'))
            print("\n--- Получены данные о погоде ---")
            for key, value in weather_data.items():
                print(f"{key.capitalize():<15}: {value}")
            print("---------------------------------")
        else:
            print("Не получено данных от сервера.")
            
    except FileNotFoundError:
        print(f"Ошибка: файл сокета не найден. Убедитесь, что сервис запущен.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        client_socket.close()
        print("Соединение закрыто.")

if __name__ == "__main__":
    main()
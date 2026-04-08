import socket
import json
import random

def start_server():
    HOST = '127.0.0.1'
    PORT = 8081
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server is running on http://{HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        try:
            # รับข้อมูล Request
            raw_request = client_socket.recv(4096).decode('utf-8')
            if not raw_request:
                continue

            # ตรวจสอบว่าเป็น Path ที่เราต้องการหรือไม่
            if "GET /roll_dice" in raw_request:
                # แยกส่วน Body ของ JSON ออกมา (อยู่หลัง \r\n\r\n)
                try:
                    parts = raw_request.split("\r\n\r\n")
                    body = parts[1] if len(parts) > 1 else "{}"
                    data = json.loads(body)
                    
                    probs = data.get("probabilities", [1/6]*6)
                    count = data.get("number_of_random", 1)
                    
                    # Logic: Biased Dice
                    faces = [1, 2, 3, 4, 5, 6]
                    results = random.choices(faces, weights=probs, k=count)
                    
                    response_json = json.dumps({"results": results})
                    
                    # สร้าง HTTP Response ให้ถูกต้องตามมาตรฐาน (Content-Length สำคัญมาก)
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Length: {len(response_json)}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        f"{response_json}"
                    )
                except Exception as e:
                    print(f"JSON/Logic Error: {e}")
                    response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

            client_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Socket Error: {e}")
        finally:
            client_socket.close() # ปิดการเชื่อมต่อให้เรียบร้อย

if __name__ == "__main__":
    start_server()
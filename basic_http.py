import socket
import json
import random

# --- CONFIGURATION ---
HOST = '127.0.0.1'
PORT = 8081

def start_server():
    # สร้าง Socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ช่วยให้รัน Server ซ้ำได้ทันทีโดยไม่ติด Error: Address already in use
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server is listening on http://{HOST}:{PORT}...")

    while True:
        client_socket, addr = server_socket.accept()
        try:
            # รับข้อมูล Request จาก Client
            request = client_socket.recv(4096).decode('utf-8')
            if not request:
                continue

            # ตรวจสอบ Path ว่าเรียกไปที่ /roll_dice หรือไม่
            if "GET /roll_dice" in request:
                # แยกส่วน Body ของ HTTP เพื่อเอา JSON (probabilities)
                try:
                    parts = request.split("\r\n\r\n")
                    if len(parts) > 1 and parts[1].strip():
                        data = json.loads(parts[1])
                        probs = data.get("probabilities", [1/6]*6)
                        count = data.get("number_of_random", 1)
                    else:
                        # ค่า Default หาก Client ไม่ได้ส่ง JSON มา
                        probs = [0.1, 0.2, 0.3, 0.1, 0.2, 0.1]
                        count = 10
                    
                    # Logic: การสุ่มลูกเต๋าแบบถ่วงน้ำหนัก
                    faces = [1, 2, 3, 4, 5, 6]
                    results = random.choices(faces, weights=probs, k=count)
                    
                    response_data = {"status": "success", "results": results}
                except Exception as e:
                    response_data = {"status": "error", "message": str(e)}

                response_json = json.dumps(response_data)

                # สร้าง HTTP Response แบบสะอาด (ห้ามใช้ Triple Quotes)
                status_line = "HTTP/1.1 200 OK\r\n"
                headers = "Content-Type: application/json\r\n"
                headers += f"Content-Length: {len(response_json)}\r\n"
                headers += "Connection: close\r\n\r\n" # \r\n\r\n คือบรรทัดว่างก่อนเริ่ม JSON
                
                response = status_line + headers + response_json

            elif "GET /" in request:
                # หน้า Home ปกติ
                body = "<html><body><h1>Biased Dice API is running!</h1><p>Try /roll_dice</p></body></html>"
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(body)}\r\n\r\n{body}"
            
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"

            client_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Server Error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
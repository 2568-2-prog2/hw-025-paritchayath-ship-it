import socket
import json
import random

class BiasedDiceServer:
    def __init__(self, host='127.0.0.1', port=8081):
        self.host = host
        self.port = port
        self.faces = [1, 2, 3, 4, 5, 6]

    def roll_dice(self, weights, count):
        # ตรวจสอบเผื่อกรณี weights เป็น None หรือยาวไม่ครบ 6
        if not weights or len(weights) != 6:
            weights = [1/6] * 6
        return random.choices(self.faces, weights=weights, k=count)

    def create_http_response(self, data, status_code="200 OK"):
        response_json = json.dumps(data)
        # สร้าง Response ตามมาตรฐาน HTTP เป๊ะๆ เพื่อกัน ConnectionReset
        response = (
            f"HTTP/1.1 {status_code}\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(response_json)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{response_json}"
        )
        return response

    def handle_client(self, client_socket):
        try:
            # รับข้อมูล (เพิ่ม buffer เป็น 8192 เพื่อความชัวร์)
            raw_request = client_socket.recv(8192).decode('utf-8')
            if not raw_request:
                return

            if "GET /roll_dice" in raw_request:
                # --- ส่วนที่สำคัญที่สุด: การแกะ Body JSON จาก Request ---
                try:
                    # HTTP แยก Header กับ Body ด้วย \r\n\r\n
                    parts = raw_request.split("\r\n\r\n")
                    body_str = parts[1].strip() if len(parts) > 1 else "{}"
                    
                    # ถ้า body_str ว่าง ให้ใช้ค่า default
                    data = json.loads(body_str) if body_str else {}
                    
                    probs = data.get("probabilities", [1/6]*6)
                    count = data.get("number_of_random", 1)

                    results = self.roll_dice(probs, count)
                    response = self.create_http_response({"results": results})
                
                except Exception as e:
                    print(f"Internal Error (JSON/Logic): {e}")
                    response = self.create_http_response({"error": str(e)}, "400 Bad Request")
            else:
                response = self.create_http_response({"error": "Not Found"}, "404 Not Found")

            client_socket.sendall(response.encode('utf-8'))
        
        except Exception as e:
            print(f"Socket Error: {e}")
        finally:
            client_socket.close()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"OOP Server started at http://{self.host}:{self.port}")
        print("Waiting for test_suite.py...")

        while True:
            client_socket, addr = server_socket.accept()
            self.handle_client(client_socket)

if __name__ == "__main__":
    server = BiasedDiceServer()
    server.start()
import unittest
import requests

class DiceTest(unittest.TestCase):
    def test_bias_accuracy(self):
        url = "http://127.0.0.1:8081/roll_dice"
        # ทดสอบโดยเน้นหน้า 6 (น้ำหนัก 0.5)
        payload = {
            "probabilities": [0.1, 0.1, 0.1, 0.1, 0.1, 0.5],
            "number_of_random": 1000
        }
        
        response = requests.get(url, json=payload)
        results = response.json()["results"]
        
        # นับจำนวนครั้งที่ออกหน้า 6
        count_six = results.count(6)
        actual_prob = count_six / 1000
        
        # เช็คว่าใกล้เคียง 0.5 หรือไม่ (อนุโลมความคลาดเคลื่อน 0.1)
        self.assertAlmostEqual(actual_prob, 0.5, delta=0.1)
        print(f"Test Passed: Face 6 appeared {count_six} times (Prob: {actual_prob})")

if __name__ == '__main__':
    unittest.main()
import unittest
import sys
sys.path.append("..")  # Üst dizini modül arama yoluna ekleyin
from data_processing import calculate_daily_total_radiation, calculate_solar_energy_potential

class TestDataProcessing(unittest.TestCase):

    def test_calculate_daily_total_radiation_empty_data(self):
        data = {}  # Boş veri
        result = calculate_daily_total_radiation(data)
        self.assertEqual(result, [])  # Boş liste bekleniyor

    def test_calculate_daily_total_radiation_valid_data(self):
        # NASA POWER API'den alınan örnek veri (gerçekçi bir örnek kullanın)
        data = {
            "properties": {
                "parameter": {
                    "ALLSKY_SFC_SW_DWN": {
                        "20231015": {
                            "00": 100, "01": 110, "02": 120,
                            "03": 130, "04": 140, "05": 150,
                            "06": 160, "07": 170, "08": 180,
                            "09": 190, "10": 200, "11": 210,
                            "12": 220, "13": 230, "14": 240,
                            "15": 250, "16": 240, "17": 230,
                            "18": 220, "19": 210, "20": 200,
                            "21": 190, "22": 180, "23": 170
                        },
                        "20231016": {
                            "00": 105, "01": 115, "02": 125,
                            "03": 135, "04": 145, "05": 155,
                            "06": 165, "07": 175, "08": 185,
                            "09": 195, "10": 205, "11": 215,
                            "12": 225, "13": 235, "14": 245,
                            "15": 255, "16": 245, "17": 235,
                            "18": 225, "19": 215, "20": 205,
                            "21": 195, "22": 185, "23": 175
                        }
                    }
                }
            }
        }
        result = calculate_daily_total_radiation(data)
        self.assertTrue(len(result) > 0)  # Sonuç listesinin boş olmaması bekleniyor
        self.assertEqual(result[0][1], 3910)  # 20231015 için beklenen toplam
        self.assertEqual(result[1][1], 4060)  # 20231016 için beklenen toplam


    def test_calculate_solar_energy_potential_valid_data(self):
        total_radiation = 2800  # Örnek günlük toplam radyasyon
        sun_hour = 5  # Örnek güneşlenme saati
        panel_efficiency = 0.2  # Örnek panel verimliliği
        panel_area = 10  # Örnek panel alanı
        result = calculate_solar_energy_potential(total_radiation, sun_hour, panel_efficiency, panel_area)
        self.assertEqual(result, 2800.0)  # Beklenen enerji potansiyeli

if __name__ == '__main__':
    unittest.main()
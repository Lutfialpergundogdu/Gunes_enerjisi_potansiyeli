import requests

def get_nasa_power_data(latitude, longitude, start_date, end_date):
    """
    NASA Power Project API'den belirtilen konum ve tarih aralığı için 
    güneş radyasyonu verilerini çeker.

    Args:
        latitude: Enlem (float).
        longitude: Boylam (float).
        start_date: Başlangıç tarihi (YYYYMMDD formatında string).
        end_date: Bitiş tarihi (YYYYMMDD formatında string).

    Returns:
        JSON formatında güneş radyasyonu verileri veya hata durumunda None.
    """

    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start": start_date,
        "end": end_date,
        "community": "RE",  # Yenilenebilir Enerji topluluğu
        "parameters": "ALLSKY_SFC_SW_DWN",  # Toplam yüzey güneş radyasyonu
        "format": "json"  # 
    }

    try:
        response = requests.get(url, params=params, timeout=10)  # Zaman aşımı süresi 
        response.raise_for_status()  # 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API isteği hatası: {e}")
        return None
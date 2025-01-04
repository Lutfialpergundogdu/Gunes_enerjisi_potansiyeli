def calculate_daily_total_radiation(hourly_data):
    """
    Saatlik güneş radyasyonu verilerini kullanarak günlük toplam 
    radyasyonu hesaplar.

    Args:
      hourly_data: API'den alınan saatlik veriler (JSON formatında).

    Returns:
      Günlük toplam radyasyon değerlerini içeren bir liste.
    """
    daily_totals = {}
    try:
        for date_hour, value in hourly_data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"].items():
            date = date_hour[:8]  
            if date not in daily_totals:
                daily_totals[date] = 0
            daily_totals[date] += value
        return list(daily_totals.items())  
    except KeyError as e:
        print(f"Hata: {e}")
        return None


def calculate_solar_energy_potential(daily_total_radiation, cloud_cover, panel_efficiency, panel_area):
    """
    Güneş enerjisi potansiyelini hesaplar.

    Args:
      daily_total_radiation: Günlük toplam güneş radyasyonu (Wh/m^2).
      cloud_cover: Bulutluluk oranı (%).
      panel_efficiency: Panel verimliliği (0 ile 1 arasında).
      panel_area: Panel alanı (m^2).

    Returns:
      Günlük enerji üretimi (Wh).
    """

    corrected_radiation = daily_total_radiation * (1 - cloud_cover / 100)

    daily_energy = corrected_radiation * panel_efficiency * panel_area
    return daily_energy
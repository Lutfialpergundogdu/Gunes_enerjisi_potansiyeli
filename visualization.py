import matplotlib.pyplot as plt

def plot_daily_total_radiation(daily_totals):
    """
    Günlük toplam radyasyon değerlerini çizgi grafiği olarak çizer.

    Args:
    daily_totals: Günlük toplam radyasyon değerlerini içeren bir liste.
    """
    if daily_totals:  
        dates, values = zip(*daily_totals)  

        plt.plot(dates, values)
        plt.xlabel("Tarih")
        plt.ylabel("Günlük Toplam Radyasyon (Wh/m^2)")
        plt.title("Günlük Toplam Güneş Radyasyonu")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("Grafik çizilemedi. Veriler eksik veya hatalı.")


def plot_ai_predictions(predictions, dates):
    """
    Yapay zeka tahminlerini çizgi grafiği olarak çizer.

    Args:
      predictions: Yapay zeka tarafından tahmin edilen değerlerin listesi.
      dates: Tahminlerin yapıldığı tarihlerin listesi.
    """
    plt.plot(dates, predictions)
    plt.xlabel("Tarih")
    plt.ylabel("Tahmini Günlük Toplam Radyasyon (Wh/m^2)")
    plt.title("Yapay Zeka Tahminleri")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview
from data_collection import get_nasa_power_data
from data_processing import calculate_daily_total_radiation, calculate_solar_energy_potential
from visualization import plot_daily_total_radiation
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Kullanıcı veritabanı oluşturma
def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Panel verimliliğini panel türüne göre hesaplama
def get_panel_efficiency(panel_type):
    efficiencies = {
        "Monokristal": 0.18,  # Monokristal için örnek verimlilik
        "Polikristal": 0.15,
        "İnce Film": 0.12
    }
    return efficiencies.get(panel_type, 0.15)  # Varsayılan olarak Polikristal verimliliği

# Veritabanını oluştur
create_database()

# Ana fonksiyon
def main():
    root = tk.Tk()
    root.title("Güneş Enerjisi Potansiyeli ve Yapay Zeka Tahmini")
    root.geometry("1200x800")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Login Frame
    login_frame = ttk.Frame(notebook)
    notebook.add(login_frame, text="Kayıt/Oturum Aç")

    username_label = ttk.Label(login_frame, text="Kullanıcı Adı:")
    username_label.grid(row=0, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(login_frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = ttk.Label(login_frame, text="Şifre:")
    password_label.grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(login_frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    logged_in = [False]

    def register_user():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve şifre girmelisiniz.")
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, 'user'))
            conn.commit()
            messagebox.showinfo("Başarılı", "Kayıt başarılı!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten kayıtlı.")
        finally:
            conn.close()

    def login_user():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Hata", "Kullanıcı adı ve şifre girmelisiniz.")
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            logged_in[0] = True
            messagebox.showinfo("Başarılı", "Oturum açıldı!")
            notebook.select(map_frame)
        else:
            messagebox.showerror("Hata", "Hatalı kullanıcı adı veya şifre.")

    register_button = ttk.Button(login_frame, text="Kayıt Ol", command=register_user)
    register_button.grid(row=2, column=0, padx=5, pady=10)

    login_button = ttk.Button(login_frame, text="Oturum Aç", command=login_user)
    login_button.grid(row=2, column=1, padx=5, pady=10)

    # Map Frame
    map_frame = ttk.Frame(notebook)
    notebook.add(map_frame, text="Harita")

    map_widget = tkintermapview.TkinterMapView(map_frame, width=780, height=550)
    map_widget.set_position(40.1568, 26.4113)
    map_widget.set_zoom(10)
    map_widget.pack(expand=True, fill="both")

    def select_location():
        position = map_widget.get_position()
        print(f"Seçilen konum: {position}")

    select_button = ttk.Button(map_frame, text="Konum Seç", command=select_location)
    select_button.pack(pady=10)

    # Analyze Frame
    analyze_frame = ttk.Frame(notebook)
    notebook.add(analyze_frame, text="Analiz")

    start_date = tk.StringVar(value="2023-10-15")
    end_date = tk.StringVar(value="2023-10-22")

    start_date_label = ttk.Label(analyze_frame, text="Başlangıç Tarihi (YYYY-MM-DD):")
    start_date_label.grid(row=0, column=0, padx=5, pady=5)
    start_date_entry = ttk.Entry(analyze_frame, textvariable=start_date)
    start_date_entry.grid(row=0, column=1, padx=5, pady=5)

    end_date_label = ttk.Label(analyze_frame, text="Bitiş Tarihi (YYYY-MM-DD):")
    end_date_label.grid(row=1, column=0, padx=5, pady=5)
    end_date_entry = ttk.Entry(analyze_frame, textvariable=end_date)
    end_date_entry.grid(row=1, column=1, padx=5, pady=5)

    panel_area_label = ttk.Label(analyze_frame, text="Panel Alanı (m^2):")
    panel_area_label.grid(row=2, column=0, padx=5, pady=5)
    panel_area_entry = ttk.Entry(analyze_frame)
    panel_area_entry.grid(row=2, column=1, padx=5, pady=5)

    panel_type_label = ttk.Label(analyze_frame, text="Panel Türü:")
    panel_type_label.grid(row=3, column=0, padx=5, pady=5)

    panel_types = ["Monokristal", "Polikristal", "İnce Film"]
    panel_type_var = tk.StringVar(analyze_frame)
    panel_type_dropdown = ttk.Combobox(analyze_frame, textvariable=panel_type_var, values=panel_types)
    panel_type_dropdown.grid(row=3, column=1, padx=5, pady=5)

    results_frame = ttk.Frame(analyze_frame)
    results_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    results_scrollbar = ttk.Scrollbar(results_frame)
    results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_text = tk.Text(results_frame, wrap=tk.WORD, yscrollcommand=results_scrollbar.set)
    results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    results_scrollbar.config(command=results_text.yview)

    # Yapay Zeka Tahminleri ve Grafikler Frame
    ai_frame = ttk.Frame(notebook)
    notebook.add(ai_frame, text="Yapay Zeka Tahminleri")

    ai_graph_frame = ttk.Frame(ai_frame)
    ai_graph_frame.pack(expand=True, fill=tk.BOTH)  # Grafik ekranın üst yarısını kaplar

    ai_results_frame = ttk.Frame(ai_frame)
    ai_results_frame.pack(expand=True, fill=tk.BOTH)  # Tahminler ekranın alt yarısını kaplar

    ai_results_label = ttk.Label(ai_results_frame, text="Yapay Zeka Tahminleri")
    ai_results_label.pack(pady=5)

    ai_results_text = tk.Text(ai_results_frame, wrap=tk.WORD, height=10)
    ai_results_text.pack(expand=True, fill="both", padx=5, pady=5)

    def analyze_location(coordinates, start_date, end_date, panel_type, panel_area, results_text):
        try:
            latitude, longitude = coordinates

            try:
                panel_area = float(panel_area)
            except ValueError:
                results_text.delete("1.0", tk.END)
                results_text.insert(tk.END, "Panel alanı geçerli bir sayı olmalıdır.")
                return

            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                results_text.delete("1.0", tk.END)
                results_text.insert(tk.END, "Tarih formatı geçersiz. Lütfen yyyy-mm-dd formatında girin.")
                return

            panel_efficiency = get_panel_efficiency(panel_type)

            data = get_nasa_power_data(latitude, longitude, start_date_obj.strftime("%Y%m%d"), end_date_obj.strftime("%Y%m%d"))

            if data:
                daily_totals = calculate_daily_total_radiation(data)

                results_text.delete("1.0", tk.END)
                results_text.insert(tk.END, "Günlük toplam radyasyon:\n")

                for date, total_radiation in daily_totals:
                    date_str = datetime.strptime(str(date), "%Y%m%d").strftime("%Y-%m-%d")
                    results_text.insert(tk.END, f"{date_str}: {total_radiation:.2f} Wh/m^2\n")

                results_text.insert(tk.END, "\nGünlük enerji üretimi:\n")
                for date, total_radiation in daily_totals:
                    daily_energy = calculate_solar_energy_potential(total_radiation, 0, panel_efficiency, panel_area)
                    results_text.insert(tk.END, f"{date_str}: {daily_energy:.2f} Wh\n")

                plot_daily_total_radiation(daily_totals)
                perform_ai_analysis(daily_totals, ai_results_text)
            else:
                results_text.delete("1.0", tk.END)
                results_text.insert(tk.END, "Veriler alınamadı.")
        except ValueError as e:
            results_text.delete("1.0", tk.END)
            results_text.insert(tk.END, f"Hatalı giriş: {e}")

    def perform_ai_analysis(daily_totals, ai_results_text):
        def run_ai_analysis():
            try:
                dates = [datetime.strptime(d, "%Y%m%d") for d, _ in daily_totals]
                radiation_values = [v for _, v in daily_totals]

                model = LinearRegression()
                X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
                y = np.array(radiation_values)
                model.fit(X, y)

                future_days = 7
                future_dates = [(dates[-1] + timedelta(days=i + 1)).strftime("%Y-%m-%d") for i in range(future_days)]
                predictions = model.predict(np.array([(len(dates) + i) for i in range(future_days)]).reshape(-1, 1))

                # Yapay Zeka Tahminlerini Text kutusuna ekle
                ai_results_text.delete(1.0, tk.END)
                ai_results_text.insert(tk.END, "AI Model Sonuçları (Tahminler):\n")
                for date, prediction in zip(future_dates, predictions):
                    ai_results_text.insert(tk.END, f"{date}: {prediction:.2f} Wh/m^2\n")

                # Grafik gösterme (ana thread'de)
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.plot(dates, radiation_values, label="Gerçek Veri", color="blue")
                ax.plot([dates[-1] + timedelta(days=i) for i in range(1, future_days + 1)], predictions, label="Tahminler", color="red", linestyle="--")

                ax.set_xlabel('Tarih')
                ax.set_ylabel('Radyasyon (Wh/m^2)')
                ax.set_title('Yapay Zeka İle Güneş Enerjisi Radyasyon Tahmini')
                ax.legend()

                canvas = FigureCanvasTkAgg(fig, ai_graph_frame)
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                canvas.draw()

            except Exception as e:
                ai_results_text.delete(1.0, tk.END)
                ai_results_text.insert(tk.END, f"Yapay Zeka analizi hatası: {e}")

        # Ana thread'de çalıştırmak için:
        root.after(0, run_ai_analysis)

    analyze_button = ttk.Button(analyze_frame, text="Analiz Yap", command=lambda: analyze_location(
        (40.1568, 26.4113), start_date.get(), end_date.get(), panel_type_var.get(), panel_area_entry.get(), results_text))
    analyze_button.grid(row=4, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

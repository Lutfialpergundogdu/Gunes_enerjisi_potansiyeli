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

create_database()

def main():
    root = tk.Tk()
    root.title("Güneş Enerjisi Potansiyeli ve Yapay Zeka Tahmini")
    root.geometry("1200x800")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

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

    ai_results_frame = ttk.Frame(analyze_frame)
    ai_results_frame.place(relx=0.75, rely=0.0, relwidth=0.25, relheight=0.5)

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
        try:
            dates = [datetime.strptime(d, "%Y%m%d") for d, _ in daily_totals]
            radiation_values = [v for _, v in daily_totals]

            model = LinearRegression()
            X = np.array([(d - dates[0]).days for d in dates]).reshape(-1, 1)
            y = np.array(radiation_values)
            model.fit(X, y)

            future_days = 7
            future_dates = [(dates[-1] + timedelta(days=i + 1)) for i in range(future_days)]
            future_X = np.array([(d - dates[0]).days for d in future_dates]).reshape(-1, 1)
            predictions = model.predict(future_X)

            ai_results_text.delete("1.0", tk.END)
            ai_results_text.insert(tk.END, "Tahminler:\n")

            for i, prediction in enumerate(predictions):
                ai_results_text.insert(tk.END, f"{future_dates[i].strftime('%Y-%m-%d')}: {prediction:.2f} Wh/m^2\n")

        except Exception as e:
            ai_results_text.delete("1.0", tk.END)
            ai_results_text.insert(tk.END, f"Hata: {str(e)}")

    calculate_button = ttk.Button(analyze_frame, text="Hesapla", command=lambda: analyze_location(
        map_widget.get_position(), start_date.get(), end_date.get(),
        panel_type_var.get(), panel_area_entry.get(), results_text
    ))
    calculate_button.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

    def check_login(event=None):
        if not logged_in[0]:
            selected_tab = notebook.index(notebook.select())
            if selected_tab != 0:
                notebook.select(0)
                messagebox.showwarning("Uyarı", "Lütfen önce giriş yapın.")

    notebook.bind("<<NotebookTabChanged>>", check_login)

    root.mainloop()

def get_panel_efficiency(panel_type):
    panel_efficiencies = {
        "Monokristal": 0.20,
        "Polikristal": 0.15,
        "İnce Film": 0.10
    }
    return panel_efficiencies.get(panel_type, 0.15)

if __name__ == "__main__":
    main()

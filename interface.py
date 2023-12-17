import tkinter as tk
from tkinter import ttk
import numpy as np

import main


def update_sliders(slider, sliders):
    total = sum(s.get() for s in sliders)
    if total != 0:
        for s in sliders:
            s.set(s.get() / total)


def run_generator():
    desired_amount = int(num_rows_entry.get())
    payment_info = [i.get() for i in net_sliders]
    banks_info = [j.get() for j in bank_prob_sliders]
    payment_info = np.array(payment_info) / sum(payment_info)
    banks_info = np.array(banks_info) / sum(banks_info)
    main.generate(desired_amount, banks_info, payment_info)

def on_key_press(event):
    char = event.char
    if not (char.isdigit() or event.keysym == "BackSpace"):
        return "break"

# Создание главного окна
root = tk.Tk()
root.title("Генератор таблицы")

# Создание рамок
bank_frame = ttk.LabelFrame(root, text="Шанс банка")
bank_frame.grid(row=0, column=0, padx=10, pady=10)

net_frame = ttk.LabelFrame(root, text="Шанс платежной системы")
net_frame.grid(row=0, column=1, padx=10, pady=10)

# Создание слайдеров для платежной системы
bank_prob_sliders = []

bank_prob_sliders.append(
    tk.Scale(bank_frame, label="Сбер", from_=0, to=1, resolution=0.01, orient="horizontal"))
bank_prob_sliders.append(
    tk.Scale(bank_frame, label="Тиньк", from_=0, to=1, resolution=0.01, orient="horizontal"))
bank_prob_sliders.append(
    tk.Scale(bank_frame, label="Альфа", from_=0, to=1, resolution=0.01, orient="horizontal"))
bank_prob_sliders.append(
    tk.Scale(bank_frame, label="Райф", from_=0, to=1, resolution=0.01, orient="horizontal"))
bank_prob_sliders.append(
    tk.Scale(bank_frame, label="ВТБ", from_=0, to=1, resolution=0.01, orient="horizontal"))

for slider in bank_prob_sliders:
    slider.pack()
print(bank_prob_sliders[0].config)
# Создание слайдеров для банка
net_sliders = []

net_sliders.append(tk.Scale(net_frame, label="Виза", from_=0, to=1, resolution=0.01, orient="horizontal"))
net_sliders.append(tk.Scale(net_frame, label="Мастеркард", from_=0, to=1, resolution=0.01, orient="horizontal"))
net_sliders.append(tk.Scale(net_frame, label="Маэстро", from_=0, to=1, resolution=0.01, orient="horizontal"))
net_sliders.append(tk.Scale(net_frame, label="МИР", from_=0, to=1, resolution=0.01, orient="horizontal"))

for slider in net_sliders:
    slider.pack()

# Поле для ввода "Количество строк"
num_rows_label = tk.Label(root, text="Количество строк:")
num_rows_label.grid(row=1, column=0, padx=10, pady=5)
num_rows_entry = tk.Entry(root)
num_rows_entry.grid(row=1, column=1, padx=10, pady=5)
num_rows_entry.bind("<Key>", on_key_press)


# num_rows = int(num_rows_entry.get())  # Получаем количество строк из поля ввода
# Кнопка Generate
generate_button = tk.Button(root, text="Generate",
                            command=run_generator)
generate_button.grid(row=2, columnspan=2)

# Привязываем обновление слайдеров к изменению общего шанса
for slider in bank_prob_sliders:
    slider.config(command=lambda s=slider: update_sliders(s, bank_prob_sliders))
    slider.set(1 / len(bank_prob_sliders))  # Устанавливаем равное дефолтное значение

for slider in net_sliders:
    slider.config(command=lambda s=slider: update_sliders(s, net_sliders))
    slider.set(1 / len(net_sliders))
root.mainloop()

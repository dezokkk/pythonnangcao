import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# Window setup
win = tk.Tk()
win.title("Calculator")
win.geometry("800x500")
win.resizable(False, False)
win.configure(bg='#f0f0f0')

# Style configuration
style = ttk.Style()
style.theme_use('clam')

# Configure styles
style.configure('Custom.TButton',
                padding=10,
                font=('Arial', 12, 'bold'))

style.configure('Custom.TLabel',
                font=('Arial', 12),
                background='#f0f0f0')

style.configure('Result.TLabel',
                font=('Arial', 14, 'bold'),
                background='#f0f0f0',
                foreground='#2c3e50')

# Configure Treeview style
style.configure("Treeview",
                background="#ffffff",
                fieldbackground="#ffffff",
                rowheight=25)
style.configure("Treeview.Heading",
                font=('Arial', 10, 'bold'),
                background="#4a90e2",
                foreground="white")
style.map("Treeview",
          background=[('selected', '#4a90e2')])

# Create main frame with padding
main_frame = ttk.Frame(win, padding="20")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Calculator frame (left side)
calc_frame = ttk.Frame(main_frame)
calc_frame.grid(row=0, column=0, padx=10, sticky='n')

# History frame (right side)
history_frame = ttk.LabelFrame(main_frame, text="Lịch sử tính toán", padding="10")
history_frame.grid(row=0, column=1, padx=10, sticky='nsew')

# History list with improved styling
history_tree = ttk.Treeview(history_frame, 
                           columns=('Time', 'Calculation', 'Result'), 
                           show='headings', 
                           height=15)

# Configure history columns
history_tree.heading('Time', text='Thời gian')
history_tree.heading('Calculation', text='Phép tính')
history_tree.heading('Result', text='Kết quả')

history_tree.column('Time', width=100)
history_tree.column('Calculation', width=150)
history_tree.column('Result', width=100)

history_tree.grid(row=0, column=0, pady=5, sticky='nsew')

# Add scrollbar to history
scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
scrollbar.grid(row=0, column=1, sticky='ns')
history_tree.configure(yscrollcommand=scrollbar.set)

# Input fields
ttk.Label(calc_frame, text="Số a:", style='Custom.TLabel').grid(column=0, row=0, sticky='w', pady=10)
so_a = tk.StringVar()
so_a_entered = ttk.Entry(calc_frame, width=15, textvariable=so_a, font=('Arial', 12))
so_a_entered.grid(column=1, row=0, padx=10, pady=10)

ttk.Label(calc_frame, text="Số b:", style='Custom.TLabel').grid(column=0, row=1, sticky='w', pady=10)
so_b = tk.StringVar()
so_b_entered = ttk.Entry(calc_frame, width=15, textvariable=so_b, font=('Arial', 12))
so_b_entered.grid(column=1, row=1, padx=10, pady=10)

# Result label
ket_qua_label = ttk.Label(calc_frame, text="Kết quả: ", style='Result.TLabel')
ket_qua_label.grid(column=0, row=3, sticky='w', columnspan=4, pady=20)

def add_to_history(calculation, result):
    """Add calculation to history"""
    current_time = datetime.now().strftime('%H:%M:%S')
    history_tree.insert('', 0, values=(current_time, calculation, result))
    
    # Keep only last 100 calculations
    if len(history_tree.get_children()) > 100:
        history_tree.delete(history_tree.get_children()[-1])

def is_number(gia_tri):
    try:
        float(gia_tri)
        return True
    except ValueError:
        return False

def format_result(value):
    # Format number to remove trailing zeros after decimal point
    return f"{value:.6f}".rstrip('0').rstrip('.')

def perform_calculation(operation):
    if not is_number(so_a.get()) or not is_number(so_b.get()):
        messagebox.showerror("Lỗi nhập liệu", "Vui lòng chỉ nhập giá trị số")
        return None
    
    a = float(so_a.get())
    b = float(so_b.get())
    
    if operation == '+':
        return a + b, f"{a} + {b}"
    elif operation == '-':
        return a - b, f"{a} - {b}"
    elif operation == '×':
        return a * b, f"{a} × {b}"
    elif operation == '÷':
        if b == 0:
            messagebox.showerror("Lỗi", "Không thể chia cho 0")
            return None
        return a / b, f"{a} ÷ {b}"

def calculate(operation):
    result = perform_calculation(operation)
    if result:
        value, expression = result
        formatted_result = format_result(value)
        ket_qua_label.configure(text=f"Kết quả: {formatted_result}")
        add_to_history(expression, formatted_result)
        
        # Clear inputs after calculation
        so_a.set("")
        so_b.set("")
        so_a_entered.focus()

def clear_history():
    """Clear all history"""
    history_tree.delete(*history_tree.get_children())

# Create frame for buttons
button_frame = ttk.Frame(calc_frame)
button_frame.grid(row=2, column=0, columnspan=4, pady=20)

# Button styling
button_style = {'width': 5, 'style': 'Custom.TButton', 'padding': 10}

# Create and position calculator buttons
buttons = [
    ('+', lambda: calculate('+')),
    ('-', lambda: calculate('-')),
    ('×', lambda: calculate('×')),
    ('÷', lambda: calculate('÷'))
]

for i, (symbol, command) in enumerate(buttons):
    btn = ttk.Button(button_frame, text=symbol, command=command, **button_style)
    btn.grid(row=i//2, column=i%2, padx=5, pady=5)

# Add clear history button
clear_button = ttk.Button(history_frame, text="Xóa lịch sử", command=clear_history)
clear_button.grid(row=1, column=0, pady=10)

# Configure grid weights
win.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Focus on first entry
so_a_entered.focus()

win.mainloop()
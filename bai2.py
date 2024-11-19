import tkinter as tk
from tkinter import ttk
import psycopg2
from tkinter import messagebox


cua_so = tk.Tk()
cua_so.title("Quản lý Sinh Viên")
cua_so.geometry("800x600")  
cua_so.configure(bg='#f0f0f0')  


main_frame = ttk.Frame(cua_so, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


style = ttk.Style()
style.theme_use('clam')  
style.configure("Treeview",
                background="#ffffff",
                fieldbackground="#ffffff",
                rowheight=25)
style.configure("Treeview.Heading",
                background="#4a90e2",
                foreground="white",
                relief="flat")
style.map("Treeview",
          background=[('selected', '#4a90e2')])


tk.Label(main_frame, text="Tên:", bg='#f0f0f0', font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
nhap_ten = ttk.Entry(main_frame, width=30)
nhap_ten.grid(row=0, column=1, padx=5, pady=5)

tk.Label(main_frame, text="Tuổi:", bg='#f0f0f0', font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
nhap_tuoi = ttk.Entry(main_frame, width=30)
nhap_tuoi.grid(row=0, column=3, padx=5, pady=5)

tk.Label(main_frame, text="Giới tính:", bg='#f0f0f0', font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=5)
nhap_gioi_tinh = ttk.Entry(main_frame, width=30)
nhap_gioi_tinh.grid(row=1, column=1, padx=5, pady=5)

tk.Label(main_frame, text="Ngành học:", bg='#f0f0f0', font=('Arial', 10, 'bold')).grid(row=1, column=2, padx=5, pady=5)
nhap_nganh_hoc = ttk.Entry(main_frame, width=30)
nhap_nganh_hoc.grid(row=1, column=3, padx=5, pady=5)


class SortableTreeview(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._sort_column = None
        self._sort_reverse = False
        
      
        for col in self['columns']:
            self.heading(col, command=lambda _col=col: self.sort_by(_col))
    
    def sort_by(self, col):
        """Xắp xếp dữ liệu theo cột được chọn"""
      
        items = [(self.item(item)['values'], item) for item in self.get_children('')]
        
        
        if self._sort_column == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_reverse = False
        
        self._sort_column = col
        
       
        col_index = list(self['columns']).index(col)
        
        def sort_key(item):
            value = item[0][col_index]
         
            if col in ['ID', 'Tuổi']:
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return float('-inf')
      
            return str(value).lower()
        
        items.sort(key=sort_key, reverse=self._sort_reverse)
        
     
        for index, (values, item) in enumerate(items):
            self.move(item, '', index)
        
        
        for col_name in self['columns']:
            if col_name == col:
                self.heading(col_name, text=f"{col_name} {'↑' if not self._sort_reverse else '↓'}")
            else:
                self.heading(col_name, text=col_name)



cot = ('ID', 'Tên', 'Tuổi', 'Giới tính', 'Ngành')
bang = SortableTreeview(main_frame, columns=cot, show='headings', height=15)


bang.column('ID', width=50)
bang.column('Tên', width=200)
bang.column('Tuổi', width=100)
bang.column('Giới tính', width=100)
bang.column('Ngành', width=200)

for cot_ten in cot:
    bang.heading(cot_ten, text=cot_ten)

bang.grid(row=2, column=0, columnspan=4, padx=5, pady=20)


scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=bang.yview)
bang.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=2, column=4, sticky='ns')


style.configure('Custom.TButton',
                background='#4a90e2',
                foreground='white',
                padding=10,
                font=('Arial', 10))


nut_them = ttk.Button(main_frame, text="Thêm sinh viên", style='Custom.TButton')
nut_them.grid(row=3, column=0, padx=5, pady=10, sticky='ew')

nut_cap_nhat = ttk.Button(main_frame, text="Cập nhật thông tin", style='Custom.TButton')
nut_cap_nhat.grid(row=3, column=1, padx=5, pady=10, sticky='ew')

nut_xoa = ttk.Button(main_frame, text="Xóa sinh viên", style='Custom.TButton')
nut_xoa.grid(row=3, column=2, padx=5, pady=10, sticky='ew')

nut_tai_lai = ttk.Button(main_frame, text="Tải lại danh sách", style='Custom.TButton')
nut_tai_lai.grid(row=3, column=3, padx=5, pady=10, sticky='ew')

def ket_noi_csdl():
    try:
        ket_noi = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="123456",
            host="localhost",
            port="5432"
        )
        return ket_noi
    except Exception as e:
        print(f"Không thể kết nối cơ sở dữ liệu: {e}")
        return None
    
def them_sinh_vien():
    ket_noi = ket_noi_csdl()
    if ket_noi is None:
        messagebox.showerror("Lỗi", "Không thể kết nối cơ sở dữ liệu.")
        return
    
    ten = nhap_ten.get()
    tuoi = nhap_tuoi.get()
    gioi_tinh = nhap_gioi_tinh.get()
    nganh = nhap_nganh_hoc.get()

   
    if not ten or not tuoi or not gioi_tinh or not nganh:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
        return

    try:
        tuoi = int(tuoi)
    except ValueError:
        messagebox.showwarning("Cảnh báo", "Tuổi phải là số nguyên.")
        return

   
    con_tro = ket_noi.cursor()
    cau_lenh_kiem_tra = """
        SELECT * FROM students WHERE name = %s AND age = %s AND gender = %s AND major = %s
    """
    con_tro.execute(cau_lenh_kiem_tra, (ten, tuoi, gioi_tinh, nganh))
    ket_qua = con_tro.fetchone()
    
    if ket_qua: 
        messagebox.showerror("Lỗi", "Sinh viên với thông tin này đã tồn tại!")
        ket_noi.close()
        return

    
    cau_lenh = "INSERT INTO students (name, age, gender, major) VALUES (%s, %s, %s, %s)"
    con_tro.execute(cau_lenh, (ten, tuoi, gioi_tinh, nganh))
    
    ket_noi.commit()
    ket_noi.close()
    messagebox.showinfo("Thành công", "Đã thêm sinh viên thành công!")

nut_them.config(command=them_sinh_vien)

def cap_nhat_sinh_vien():
    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()

    sinh_vien_chon = bang.selection()[0]
    sinh_vien_id = bang.item(sinh_vien_chon, 'values')[0]

    ten = nhap_ten.get()
    tuoi = int(nhap_tuoi.get())
    gioi_tinh = nhap_gioi_tinh.get()
    nganh = nhap_nganh_hoc.get()

    cau_lenh = "UPDATE students SET name=%s, age=%s, gender=%s, major=%s WHERE id=%s"
    con_tro.execute(cau_lenh, (ten, tuoi, gioi_tinh, nganh, sinh_vien_id))

    ket_noi.commit()
    ket_noi.close()

nut_cap_nhat.config(command=cap_nhat_sinh_vien)

def chon_sinh_vien(event):
   
    selected_item = bang.selection()
    if selected_item:
        sinh_vien = bang.item(selected_item[0], 'values')
      
        nhap_ten.delete(0, tk.END)
        nhap_ten.insert(0, sinh_vien[1])
        
        nhap_tuoi.delete(0, tk.END)
        nhap_tuoi.insert(0, sinh_vien[2])
        
        nhap_gioi_tinh.delete(0, tk.END)
        nhap_gioi_tinh.insert(0, sinh_vien[3])
        
        nhap_nganh_hoc.delete(0, tk.END)
        nhap_nganh_hoc.insert(0, sinh_vien[4])

bang.bind("<<TreeviewSelect>>", chon_sinh_vien)

def xoa_sinh_vien():
    ket_noi = ket_noi_csdl()
    con_tro = ket_noi.cursor()

    sinh_vien_chon = bang.selection()[0]
    sinh_vien_id = bang.item(sinh_vien_chon, 'values')[0]

    cau_lenh = "DELETE FROM students WHERE id=%s"
    con_tro.execute(cau_lenh, (sinh_vien_id,))

    ket_noi.commit()
    ket_noi.close()

nut_xoa.config(command=xoa_sinh_vien)

def tai_lai_danh_sach():
  
    for item in bang.get_children():
        bang.delete(item)


    ket_noi = ket_noi_csdl()
    if ket_noi is None:
        messagebox.showerror("Lỗi", "Không thể kết nối cơ sở dữ liệu.")
        return
        
    con_tro = ket_noi.cursor()

    try:
      
        con_tro.execute("SELECT * FROM students ORDER BY name ASC")
        hang = con_tro.fetchall()

        for du_lieu in hang:
            bang.insert('', tk.END, values=du_lieu)

    except Exception as e:
        messagebox.showerror("Lỗi", f"Lỗi khi tải dữ liệu: {str(e)}")
    
    finally:
        ket_noi.close()

   
    bang.heading('Tên', text='Tên ↑')
   
    for col in ['ID', 'Tuổi', 'Giới tính', 'Ngành']:
        bang.heading(col, text=col)

nut_tai_lai.config(command=tai_lai_danh_sach)

cua_so.mainloop()
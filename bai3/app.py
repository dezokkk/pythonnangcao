from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from decimal import Decimal
import math
import psycopg2

app = Flask(__name__)
app.secret_key = '123456'

# Hàm kết nối cơ sở dữ liệu
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

# Route chính
@app.route('/')
def index():
    trang_hien_tai = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    so_san_pham_mot_trang = 5
    offset = (trang_hien_tai - 1) * so_san_pham_mot_trang

    ket_noi = ket_noi_csdl()
    if ket_noi is None:
        return "Không thể kết nối đến cơ sở dữ liệu."
    
    con_tro = ket_noi.cursor()
    
    # Modified queries to include search
    if search_query:
        con_tro.execute("SELECT COUNT(*) FROM products WHERE LOWER(name) LIKE LOWER(%s)", (f'%{search_query}%',))
        tong_so_san_pham = con_tro.fetchone()[0]
        
        con_tro.execute("""
            SELECT * FROM products 
            WHERE LOWER(name) LIKE LOWER(%s) 
            ORDER BY id LIMIT %s OFFSET %s
        """, (f'%{search_query}%', so_san_pham_mot_trang, offset))
    else:
        con_tro.execute("SELECT COUNT(*) FROM products")
        tong_so_san_pham = con_tro.fetchone()[0]
        
        con_tro.execute("SELECT * FROM products ORDER BY id LIMIT %s OFFSET %s", 
                       (so_san_pham_mot_trang, offset))

    tong_so_trang = (tong_so_san_pham + so_san_pham_mot_trang - 1) // so_san_pham_mot_trang
    products = con_tro.fetchall()

    con_tro.close()
    ket_noi.close()
    
    return render_template('index.html', 
                         products=products, 
                         trang_hien_tai=trang_hien_tai, 
                         tong_so_trang=tong_so_trang,
                         search_query=search_query)

# Route thêm sản phẩm
@app.route('/add', methods=['POST'])
def add_product():
    if request.method == 'POST':
        try:
            ten = request.form['name']
            gia = request.form['price'].replace(',', '.')  
            so_luong = request.form['quantity']
            mo_ta = request.form['description']

            if not ten or not gia or not so_luong:
                flash('Vui lòng điền đầy đủ thông tin', 'error')
                return redirect(url_for('index'))

            gia = float(gia)
            so_luong = int(so_luong)

            if gia < 0 or so_luong < 0:
                flash('Giá và số lượng không thể âm', 'error')
                return redirect(url_for('index'))

            ket_noi = ket_noi_csdl()
            if ket_noi is None:
                flash('Lỗi kết nối database', 'error')
                return redirect(url_for('index'))

            cur = ket_noi.cursor()
            cur.execute(
                "INSERT INTO products (name, price, quantity, description) VALUES (%s, %s, %s, %s)",
                (ten, gia, so_luong, mo_ta)
            )
            ket_noi.commit()
            flash('Thêm sản phẩm thành công!', 'success')

        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        finally:
            if ket_noi:
                ket_noi.close()

    return redirect(url_for('index'))

# Route sửa sản phẩm
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    ket_noi = ket_noi_csdl()
    if ket_noi is None:
        flash('Không thể kết nối đến cơ sở dữ liệu', 'danger')
        return redirect(url_for('index'))

    con_tro = ket_noi.cursor()
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            price = request.form['price']
            quantity = request.form['quantity']
            description = request.form['description']

            # Validation
            if not name or not price or not quantity:
                flash('Vui lòng điền đầy đủ thông tin', 'danger')
                return redirect(url_for('edit_product', id=id))

            try:
                price = float(price)
                quantity = int(quantity)
            except ValueError:
                flash('Giá và số lượng phải là số', 'danger')
                return redirect(url_for('edit_product', id=id))

            if price < 0 or quantity < 0:
                flash('Giá và số lượng không thể âm', 'danger')
                return redirect(url_for('edit_product', id=id))

            con_tro.execute("""
                UPDATE products 
                SET name=%s, price=%s, quantity=%s, description=%s 
                WHERE id=%s""",
                (name, price, quantity, description, id))
            
            ket_noi.commit()
            flash('Cập nhật sản phẩm thành công!', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            ket_noi.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('edit_product', id=id))

        finally:
            con_tro.close()
            ket_noi.close()

    # GET request - load product data
    try:
        con_tro.execute("SELECT * FROM products WHERE id=%s", (id,))
        product = con_tro.fetchone()
        
        if product is None:
            flash('Không tìm thấy sản phẩm', 'danger')
            return redirect(url_for('index'))
        
        return render_template('edit.html', product=product)

    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('index'))

    finally:
        con_tro.close()
        if ket_noi:
            ket_noi.close()

# Route xóa sản phẩm
@app.route('/delete/<int:id>')
def delete_product(id):
    ket_noi = ket_noi_csdl()
    if ket_noi is None:
        return "Không thể kết nối đến cơ sở dữ liệu."

    con_tro = ket_noi.cursor()
    con_tro.execute("DELETE FROM products WHERE id=%s", (id,))
    ket_noi.commit()

    con_tro.close()
    ket_noi.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

import tkinter as tk
from locale import windows_locale
from tkinter import messagebox
import sqlite3
from datetime import datetime


def create_connection():
    return sqlite3.connect('mall_management.db')

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    #创建商户表，包含商户名，自动分配的商户ID和余额
    cursor.execute('''CREATE TABLE IF NOT EXISTS Merchants (
        merchant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        merchant_name TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 0.0
    )''')

    #创建商铺表，包含商铺编号，商铺租用状态，商铺租金，当前租用的商户编号
    cursor.execute('''CREATE TABLE IF NOT EXISTS Shops(
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT NOT NULL,
        merchant_id NOT NULL DEFAULT 0,
        status BOOL DEFAULT false,
        rent REAL NOT NULL,
        rent_time TEXT DEFAULT '0000-00-00 00:00:00'
    )''')

    #创建交易记录表，包含交易编号，商户编号，交易类型，交易时间和交易金额
    cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions(
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    merchant_id INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, 
    transaction_time TEXT NOT NULL,
    amount REAL NOT NULL
    )''')

    # #创建租赁记录表，包含租赁编号，商户编号，商铺编号，租赁开始时间和租赁结束时间
    # cursor.execute('''CREATE TABLE IF NOT EXISTS ShopRentals (
    # rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
    # merchant_id INTEGER NOT NULL,
    # shop_id INTEGER NOT NULL,
    # start_time TEXT NOT NULL,
    # end_time TEXT NOT NULL,
    # FOREIGN KEY (merchant_id) REFERENCES Merchants(merchant_id),
    # FOREIGN KEY (shop_id) REFERENCES Shops(shop_id)
    # )''')

    conn.commit()
    conn.close()

#商户注册
def register_merchant():
    try:
        merchant_name = usr_merchant.get()

        if not merchant_name:
            raise ValueError("商户名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        #检测商户名是否已存在
        cursor.execute("SELECT * FROM Merchants WHERE merchant_name=?", (merchant_name,))
        if cursor.fetchone():
            raise ValueError("商户名已存在")

        #插入商户信息
        cursor.execute("INSERT INTO Merchants (merchant_name) VALUES (?)", (merchant_name,))
        conn.commit()
        conn.close()

        messagebox.showinfo("注册成功", "商户注册成功")
        # entry_merchant_name.delete(0, tk.END) #清空输入框
    except ValueError as e:
        messagebox.showerror("错误", str(e))

#商户登录
def login_merchant():
    try:
        merchant_name = usr_merchant.get()

        if not merchant_name:
            raise ValueError("商户名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        #检测商户名是否存在
        cursor.execute("SELECT * FROM Merchants WHERE merchant_name=?", (merchant_name,))
        if not cursor.fetchone():
            raise ValueError("商户名不存在")

        messagebox.showinfo("登录成功", "商户登录成功")
        # entry_merchant_name.delete(0, tk.END) #清空输入框
        #在这里可以添加商户登录后的操作，比如跳转到商户操作界面
        merchant_operations()
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def merchant_operations():
    #商户操作界面
    window_merchant_ops = tk.Toplevel(root)
    window_merchant_ops.title("商户操作界面")
    window_merchant_ops.geometry("400x300")
    button_check_balance = tk.Button(window_merchant_ops, text="查看余额", command=check_balance)
    button_rent_shop = tk.Button(window_merchant_ops, text="租用商铺", command=rent_shop)
    button_view_transactions = tk.Button(window_merchant_ops, text="查看交易记录", command=view_transactions)
    button_view_rentals = tk.Button(window_merchant_ops, text="查看租赁记录", command=view_rentals)
    button_recharge_balance = tk.Button(window_merchant_ops, text="充值余额", command=recharge_balance_window)
    button_unsubscribe_merchant = tk.Button(window_merchant_ops, text="注销商户", command=unsubscribe_merchant)
    button_unrent_shop = tk.Button(window_merchant_ops, text="退租商铺", command=unrent_shop)
    button_check_balance.pack(pady=5)
    button_rent_shop.pack(pady=5)
    button_unrent_shop.pack(pady=5)
    button_view_transactions.pack(pady=5)
    button_view_rentals.pack(pady=5)
    button_recharge_balance.pack(pady=5)
    button_unsubscribe_merchant.pack(pady=5)

def check_balance():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM Merchants WHERE merchant_name=?",
                   (usr_merchant.get(),))
    balance = cursor.fetchone()

    if balance:
        messagebox.showinfo("余额查询", message=f"您的余额为: {balance[0]}元")
    else:
        messagebox.showinfo("余额查询", message="您还未进行过充值！")

def rent_shop():
    windows_rent = tk.Toplevel(root)
    windows_rent.title("租用商铺")
    windows_rent.geometry("400x300")
    frame_rent = tk.Frame(windows_rent)
    frame_rent.pack(pady=20)
    label_shop_name = tk.Label(frame_rent, text="商铺名:")
    label_shop_name.pack()
    tk_shop_name = tk.StringVar()
    tk_shop_name.set("商铺名")
    entry_shop_name = tk.Entry(frame_rent, textvariable=tk_shop_name)
    entry_shop_name.pack()
    conn = create_connection()
    cursor = conn.cursor()
    shop_name = tk_shop_name.get()
    try:
        cursor.execute("SELECT rent FROM Shops WHERE status=false and shop_name=?", (shop_name,))
        rent = cursor.fetchone()
        button_rent = tk.Button(frame_rent, text="租用",
                                command=lambda: rent_shop_confirm(shop_name, rent, windows_rent, frame_rent))
        button_rent.pack()

    except ValueError as e:
        messagebox.showerror("错误", str(e))

def rent_shop_confirm(shop_name, rent, window, frame_rent):
    try:
        label_rent = tk.Label(frame_rent, text="租金:")
        label_rent.pack()
        tk_rent = tk.StringVar()
        if rent:
            tk_rent.set(f"租金：{rent}")
            label_rent.config(text=f"租金：{rent}")
        else:
            raise ValueError("商铺不存在或已被租用")

        confirm = tk.messagebox.askquestion(question="租用商铺", message=f"您确定要租用商铺 {shop_name} 吗？")
        if confirm != 'yes':
            raise ValueError("租用已取消")


        conn = create_connection()
        cursor = conn.cursor()

        # Fetch merchant ID
        cursor.execute("SELECT merchant_id FROM Merchants WHERE merchant_name=?", (usr_merchant.get(),))
        merchant_id = cursor.fetchone()
        if not merchant_id:
            raise ValueError("商户不存在")
        # Check if the merchant has enough balance
        cursor.execute("SELECT balance FROM Merchants WHERE merchant_id=?", (merchant_id[0],))
        balance = cursor.fetchone()
        if not balance or balance[0] < rent[0]:
            raise ValueError("余额不足，请充值")


        # Update shop status and assign merchant ID
        rental_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("UPDATE Shops SET status=true, merchant_id=?, rent_time=? WHERE shop_name=?", (merchant_id[0], rental_date, shop_name))

        conn.commit()
        conn.close()

        messagebox.showinfo("成功", "租用成功")
        #扣除第一个月的租金
        cursor.execute("UPDATE Merchants SET balance = balance - ? WHERE merchant_id = ?", (rent[0], merchant_id[0]))
        window.destroy()
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def unrent_shop():
    try:
        shop_name = usr_merchant.get()
        if not shop_name:
            raise ValueError("商铺名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        # Fetch merchant ID
        cursor.execute("SELECT merchant_id FROM Merchants WHERE merchant_name=?", (shop_name,))
        merchant_id = cursor.fetchone()
        if not merchant_id:
            raise ValueError("商户不存在")

        # Update shop status and remove merchant ID
        cursor.execute("UPDATE Shops SET status=false, merchant_id=0 WHERE shop_name=?", (shop_name,))

        conn.commit()
        conn.close()

        messagebox.showinfo("成功", "退租成功")
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def view_transactions():
    try:
        merchant_name = usr_merchant.get()
        if not merchant_name:
            raise ValueError("商户名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        # Fetch merchant ID
        cursor.execute("SELECT merchant_id FROM Merchants WHERE merchant_name=?", (merchant_name,))
        merchant_id = cursor.fetchone()
        if not merchant_id:
            raise ValueError("商户不存在")

        # Fetch transactions for the merchant
        cursor.execute(
            "SELECT transaction_id, transaction_type, transaction_time, amount FROM Transactions WHERE merchant_id=?",
            (merchant_id[0],))
        transactions = cursor.fetchall()
        conn.close()

        # Create a new window to display transactions
        window_transactions = tk.Toplevel(root)
        window_transactions.title("交易记录")
        window_transactions.geometry("600x400")

        tk.Label(window_transactions, text = "交易编号").grid(row=0, column=0)
        tk.Label(window_transactions, text = "交易类型").grid(row=0, column=1)
        tk.Label(window_transactions, text = "交易时间").grid(row=0, column=2)
        tk.Label(window_transactions, text = "交易金额").grid(row=0, column=3)

        for i, transaction in enumerate(transactions):
            tk.Label(window_transactions, text=transaction[0]).grid(row=i+1, column=0)
            tk.Label(window_transactions, text=transaction[1]).grid(row=i+1, column=1)
            tk.Label(window_transactions, text=transaction[2]).grid(row=i+1, column=2)
            tk.Label(window_transactions, text=transaction[3]).grid(row=i+1, column=3)

    except ValueError as e:
        messagebox.showerror("错误", str(e))

def view_rentals():
    try:
        merchant_name = usr_merchant.get()
        if not merchant_name:
            raise ValueError("商户名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        # Fetch merchant ID
        cursor.execute("SELECT merchant_id FROM Merchants WHERE merchant_name=?", (merchant_name,))
        merchant_id = cursor.fetchone()
        if not merchant_id:
            raise ValueError("商户不存在")

        # Fetch rentals for the merchant
        cursor.execute(
            "SELECT shop_name, rent, rent_time FROM Shops WHERE merchant_id=? and status=true",
            (merchant_id[0],))
        rentals = cursor.fetchall()
        conn.close()
        # Create a new window to display rentals
        window_rentals = tk.Toplevel(root)
        window_rentals.title("租赁记录")
        window_rentals.geometry("400x300")
        tk.Label(window_rentals, text = "商铺名").grid(row=0, column=0)
        tk.Label(window_rentals, text = "租金").grid(row=0, column=1)
        tk.Label(window_rentals, text = "租赁起始时间").grid(row=0, column=2)
        for i, rental in enumerate(rentals):
            tk.Label(window_rentals, text=rental[0]).grid(row=i+1, column=0)
            tk.Label(window_rentals, text=rental[1]).grid(row=i+1, column=1)
            tk.Label(window_rentals, text=rental[2]).grid(row=i+1, column=2)
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def recharge_balance_window():
    windows_recharge = tk.Toplevel(root)
    windows_recharge.title("充值界面")
    windows_recharge.geometry("150x150")
    frame_recharge = tk.Frame(windows_recharge)
    frame_recharge.pack(pady=20)
    label_amount = tk.Label(frame_recharge, text="充值金额:")
    label_amount.pack()
    tk_amount = tk.StringVar()
    tk_amount.set("0")
    entry_amount = tk.Entry(frame_recharge, textvariable=tk_amount)
    entry_amount.pack()
    button_recharge = tk.Button(frame_recharge, text="充值",command=lambda: recharge_balance((float)(tk_amount.get()), windows_recharge))
    button_recharge.pack()


def recharge_balance(amount, window):
    try:
        merchant_name = usr_merchant.get()
        if amount <= 0:
            raise ValueError("充值金额必须大于零")

        conn = create_connection()
        cursor = conn.cursor()

        merchant_id = cursor.execute("SELECT merchant_id FROM Merchants WHERE merchant_name = ?", (merchant_name,)).fetchone()[0]
        if not merchant_id:
            raise ValueError("商户ID不存在")

        # 更新商户余额
        cursor.execute("UPDATE Merchants SET balance = balance + ? WHERE merchant_name = ?",
                       (amount, merchant_name))

        # 插入充值记录
        transaction_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO Transactions (merchant_id, amount, transaction_type, transaction_time) VALUES (?, ?, ?, ?)",
            (merchant_id, amount, 'recharge', transaction_date))

        conn.commit()
        conn.close()

        messagebox.showinfo("成功", "充值成功")
        check_balance()  # 更新余额显示
        window.destroy()

    except ValueError as e:
        messagebox.showerror("错误", str(e))

def unsubscribe_merchant():
    try:
        merchant_name = usr_merchant.get()
        if not merchant_name:
            raise ValueError("商户名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        # 检查商户是否存在
        cursor.execute("SELECT * FROM Merchants WHERE merchant_name=?", (merchant_name,))
        if not cursor.fetchone():
            raise ValueError("商户名不存在")
        # 检查商户是否有未结清的租金
        cursor.execute("SELECT * FROM Shops WHERE merchant_name=?", (merchant_name,))

        #删除商户的租赁交易
        cursor.execute("DELETE FROM Transactions WHERE merchant_id=?", (merchant_name,))
        #删除商户的租赁记录
        cursor.execute("UPDATE Shops SET status=false, merchant_id=0 WHERE merchant_name=?", (merchant_name,))

        # 删除商户信息
        cursor.execute("DELETE FROM Merchants WHERE merchant_name=?", (merchant_name,))
        conn.commit()
        conn.close()


        messagebox.showinfo("注销成功", "商户注销成功")
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def shop_operations():
    #商铺操作界面
    window_shop_ops = tk.Toplevel(root)
    window_shop_ops.title("商铺操作界面")
    window_shop_ops.geometry("400x300")
    button_new_shop = tk.Button(window_shop_ops, text="新建商铺", command=new_shop)
    button_unsubscribe_shop = tk.Button(window_shop_ops, text="注销商铺", command=unsubscribe_shop)
    button_change_rent = tk.Button(window_shop_ops, text="修改租金", command=change_rent)
    button_show_all_shops = tk.Button(window_shop_ops, text="查看所有商铺", command=show_all_shops)
    button_show_all_merchants = tk.Button(window_shop_ops, text="查看所有商户", command=show_all_merchants)
    button_show_all_transactions = tk.Button(window_shop_ops, text="查看所有交易记录", command=show_all_transactions)
    button_new_shop.pack(pady=5)
    button_unsubscribe_shop.pack(pady=5)
    button_change_rent.pack(pady=5)
    button_show_all_shops.pack(pady=5)
    button_show_all_merchants.pack(pady=5)
    button_show_all_transactions.pack(pady=5)

def new_shop():
    #新建商铺界面
    window_new_shop = tk.Toplevel(root)
    window_new_shop.title("新建商铺")
    window_new_shop.geometry("400x300")
    frame_new_shop = tk.Frame(window_new_shop)
    frame_new_shop.pack(pady=20)
    label_shop_name = tk.Label(frame_new_shop, text="商铺名:")
    label_shop_name.pack()
    tk_shop_name = tk.StringVar()
    tk_shop_name.set("商铺名")
    entry_shop_name = tk.Entry(frame_new_shop, textvariable=tk_shop_name)
    entry_shop_name.pack()
    label_rent = tk.Label(frame_new_shop, text="租金:")
    label_rent.pack()
    tk_rent = tk.StringVar()
    tk_rent.set("0")
    entry_rent = tk.Entry(frame_new_shop, textvariable=tk_rent)
    entry_rent.pack()
    button_create = tk.Button(frame_new_shop, text="创建", command=lambda: create_new_shop(tk_shop_name.get(), (float)(tk_rent.get()), window_new_shop))
    button_create.pack()

def create_new_shop(shop_name, rent, window):
    try:
        if not shop_name:
            raise ValueError("商铺名不能为空")
        if rent <= 0:
            raise ValueError("租金必须大于零")

        conn = create_connection()
        cursor = conn.cursor()

        # 检查商铺名是否已存在
        cursor.execute("SELECT * FROM Shops WHERE shop_name=?", (shop_name,))
        if cursor.fetchone():
            raise ValueError("商铺名已存在")

        # 插入商铺信息
        cursor.execute("INSERT INTO Shops (shop_name, rent, rent_time, status) VALUES (?, ?, ?, ?)", (shop_name, rent, '0000-00-00 00:00:00', False))
        conn.commit()
        conn.close()

        messagebox.showinfo("创建成功", "商铺创建成功")
        window.destroy()
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def unsubscribe_shop():
    #注销商铺界面
    window_unsubscribe_shop = tk.Toplevel(root)
    window_unsubscribe_shop.title("注销商铺")
    window_unsubscribe_shop.geometry("400x300")
    frame_unsubscribe_shop = tk.Frame(window_unsubscribe_shop)
    frame_unsubscribe_shop.pack(pady=20)
    label_shop_name = tk.Label(frame_unsubscribe_shop, text="商铺名:")
    label_shop_name.pack()
    tk_shop_name = tk.StringVar()
    tk_shop_name.set("商铺名")
    entry_shop_name = tk.Entry(frame_unsubscribe_shop, textvariable=tk_shop_name)
    entry_shop_name.pack()
    button_delete = tk.Button(frame_unsubscribe_shop, text="注销", command=lambda: delete_shop(tk_shop_name.get(), window_unsubscribe_shop))
    button_delete.pack()

def delete_shop(shop_name, window):
    try:
        if not shop_name:
            raise ValueError("商铺名不能为空")

        conn = create_connection()
        cursor = conn.cursor()

        # 检查商铺名是否存在
        cursor.execute("SELECT * FROM Shops WHERE shop_name=?", (shop_name,))
        if not cursor.fetchone():
            raise ValueError("商铺名不存在")

        # 删除商铺信息
        cursor.execute("DELETE FROM Shops WHERE shop_name=?", (shop_name,))
        conn.commit()
        conn.close()

        messagebox.showinfo("注销成功", "商铺注销成功")
        window.destroy()
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def change_rent():
    #修改租金界面
    window_change_rent = tk.Toplevel(root)
    window_change_rent.title("修改租金")
    window_change_rent.geometry("400x300")
    frame_change_rent = tk.Frame(window_change_rent)
    frame_change_rent.pack(pady=20)
    label_shop_name = tk.Label(frame_change_rent, text="商铺名:")
    label_shop_name.pack()
    tk_shop_name = tk.StringVar()
    tk_shop_name.set("商铺名")
    entry_shop_name = tk.Entry(frame_change_rent, textvariable=tk_shop_name)
    entry_shop_name.pack()
    label_new_rent = tk.Label(frame_change_rent, text="新租金:")
    label_new_rent.pack()
    tk_new_rent = tk.StringVar()
    tk_new_rent.set("0")
    entry_new_rent = tk.Entry(frame_change_rent, textvariable=tk_new_rent)
    entry_new_rent.pack()
    button_update = tk.Button(frame_change_rent, text="修改", command=lambda: update_shop_rent(tk_shop_name.get(), (float)(tk_new_rent.get()), window_change_rent))
    button_update.pack()

def update_shop_rent(shop_name, new_rent, window):
    try:
        if not shop_name:
            raise ValueError("商铺名不能为空")
        if new_rent <= 0:
            raise ValueError("租金必须大于零")

        conn = create_connection()
        cursor = conn.cursor()

        # 检查商铺名是否存在
        cursor.execute("SELECT * FROM Shops WHERE shop_name=?", (shop_name,))
        if not cursor.fetchone():
            raise ValueError("商铺名不存在")

        # 更新商铺租金
        cursor.execute("UPDATE Shops SET rent=? WHERE shop_name=?", (new_rent, shop_name))
        conn.commit()
        conn.close()

        messagebox.showinfo("修改成功", "商铺租金修改成功")
        window.destroy()
    except ValueError as e:
        messagebox.showerror("错误", str(e))

def show_all_shops():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Shops")
    shops = cursor.fetchall()
    conn.close()

    # Create a new window to display shops
    window_shops = tk.Toplevel(root)
    window_shops.title("所有商铺")
    window_shops.geometry("600x400")
    tk.Label(window_shops, text="商铺编号").grid(row=0, column=0)
    tk.Label(window_shops, text="商铺名").grid(row=0, column=1)
    tk.Label(window_shops, text="商户编号").grid(row=0, column=2)
    tk.Label(window_shops, text="租用状态").grid(row=0, column=3)
    tk.Label(window_shops, text="租金").grid(row=0, column=4)
    tk.Label(window_shops, text="租用时间").grid(row=0, column=5)
    for i, shop in enumerate(shops):
        tk.Label(window_shops, text=shop[0]).grid(row=i+1, column=0)
        tk.Label(window_shops, text=shop[1]).grid(row=i+1, column=1)
        tk.Label(window_shops, text=shop[2]).grid(row=i+1, column=2)
        tk.Label(window_shops, text=shop[3]).grid(row=i+1, column=3)
        tk.Label(window_shops, text=shop[4]).grid(row=i+1, column=4)
        tk.Label(window_shops, text=shop[5]).grid(row=i+1, column=5)

def show_all_merchants():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Merchants")
    merchants = cursor.fetchall()
    conn.close()

    # Create a new window to display merchants
    window_merchants = tk.Toplevel(root)
    window_merchants.title("所有商户")
    window_merchants.geometry("400x300")
    tk.Label(window_merchants, text="商户编号").grid(row=0, column=0)
    tk.Label(window_merchants, text="商户名").grid(row=0, column=1)
    tk.Label(window_merchants, text="余额").grid(row=0, column=2)
    for i, merchant in enumerate(merchants):
        tk.Label(window_merchants, text=merchant[0]).grid(row=i+1, column=0)
        tk.Label(window_merchants, text=merchant[1]).grid(row=i+1, column=1)
        tk.Label(window_merchants, text=merchant[2]).grid(row=i+1, column=2)

def show_all_transactions():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Transactions")
    transactions = cursor.fetchall()
    conn.close()

    # Create a new window to display transactions
    window_transactions = tk.Toplevel(root)
    window_transactions.title("所有交易记录")
    window_transactions.geometry("600x400")
    tk.Label(window_transactions, text="交易编号").grid(row=0, column=0)
    tk.Label(window_transactions, text="商户编号").grid(row=0, column=1)
    tk.Label(window_transactions, text="交易类型").grid(row=0, column=2)
    tk.Label(window_transactions, text="交易时间").grid(row=0, column=3)
    tk.Label(window_transactions, text="交易金额").grid(row=0, column=4)
    for i, transaction in enumerate(transactions):
        tk.Label(window_transactions, text=transaction[0]).grid(row=i+1, column=0)
        tk.Label(window_transactions, text=transaction[1]).grid(row=i+1, column=1)
        tk.Label(window_transactions, text=transaction[2]).grid(row=i+1, column=2)
        tk.Label(window_transactions, text=transaction[3]).grid(row=i+1, column=3)
        tk.Label(window_transactions, text=transaction[4]).grid(row=i+1, column=4)

#创建图形界面
root = tk.Tk()
root.title("商场管理系统")
root.geometry("400x300")

#创建商户注册界面
frame_register = tk.Frame(root)
frame_register.pack(pady=20)

label_merchant_name = tk.Label(frame_register, text="商户名:")
label_merchant_name.grid(row=0, column=0)

usr_merchant = tk.StringVar()
entry_merchant_name = tk.Entry(frame_register, textvariable=usr_merchant)
entry_merchant_name.grid(row=0, column=1, columnspan=3)

button_register = tk.Button(frame_register, text="注册", command=register_merchant)
button_login = tk.Button(frame_register, text="登录", command=login_merchant)
button_register.grid(row=1, column=1, pady=10)
button_login.grid(row=1, column=2, pady=10)

button_shop_ops = tk.Button(frame_register, text="商铺操作", command=shop_operations)
button_shop_ops.grid(row=1, column=3, pady=10)

create_tables()
root.mainloop()

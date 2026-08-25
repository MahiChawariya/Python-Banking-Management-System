import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os
from datetime import datetime

# ---------------- DATABASE ----------------
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banking.db")

def db():
    return sqlite3.connect(DB)

def now():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

def title(win, text):
    tk.Label(win, text=text, font=("Arial",18,"bold"),
             bg="#003366", fg="white").pack(fill="x", ipady=10)

def window(text, size="350x230"):
    w=tk.Toplevel(root); w.title(text); w.geometry(size)
    w.configure(bg="#F5F9FF"); w.resizable(False,False)
    title(w,text.upper()); return w

def transaction(acc, typ, amount, cur):
    cur.execute("INSERT INTO transactions(account_no,transaction_type,amount,date_time) VALUES(?,?,?,?)",
                (acc,typ,amount,now()))

# ---------------- BALANCE ENQUIRY ----------------
def balance_enquiry(acc):
    con=db(); cur=con.cursor()
    cur.execute("SELECT account_holder_name,balance FROM users WHERE account_no=?",(acc,))
    r=cur.fetchone(); con.close()
    if r:
        messagebox.showinfo("Balance",
            f"Account Holder : {r[0]}\nAccount Number : {acc}\n\nAvailable Balance : ₹{r[1]:.2f}")
    else: messagebox.showerror("Error","Account not found")

# ---------------- DEPOSIT / WITHDRAW ----------------
def money_action(acc, typ):
    w=window(typ+" Money"); tk.Label(w,text="Enter Amount",bg="#F5F9FF").pack(pady=15)
    e=tk.Entry(w,width=25); e.pack()
    def save():
        try:
            amt=float(e.get())
            if amt<=0: raise ValueError
            con=db(); cur=con.cursor()
            cur.execute("SELECT balance FROM users WHERE account_no=?",(acc,))
            r=cur.fetchone()
            if not r:
                con.close(); messagebox.showerror("Error","Account not found"); return
            if typ=="Withdraw" and amt>r[0]:
                con.close(); messagebox.showerror("Error","Insufficient Balance"); return
            sign=-amt if typ=="Withdraw" else amt
            cur.execute("UPDATE users SET balance=balance+? WHERE account_no=?",(sign,acc))
            transaction(acc,typ,amt,cur); con.commit(); con.close()
            messagebox.showinfo("Success",f"Money {typ.lower()}ed Successfully")
            w.destroy()
        except ValueError: messagebox.showerror("Error","Enter a valid amount")
        except sqlite3.Error as ex: messagebox.showerror("Database Error",str(ex))
    tk.Button(w,text=typ,width=15,height=2,command=save).pack(pady=15)

def deposit(acc): money_action(acc,"Deposit")
def withdraw(acc): money_action(acc,"Withdraw")

# ---------------- MONEY TRANSFER ----------------
def transfer_money(acc):
    w=window("Transfer Money","380x290")
    tk.Label(w,text="Receiver Account Number",bg="#F5F9FF").pack(pady=10)
    receiver=tk.Entry(w,width=28); receiver.pack()
    tk.Label(w,text="Enter Amount",bg="#F5F9FF").pack(pady=10)
    amount=tk.Entry(w,width=28); amount.pack()
    def send():
        try:
            rec=receiver.get().strip(); amt=float(amount.get())
            if not rec or amt<=0 or rec==acc: raise ValueError
            con=db(); cur=con.cursor()
            cur.execute("SELECT balance FROM users WHERE account_no=?",(acc,)); sender=cur.fetchone()
            cur.execute("SELECT account_no FROM users WHERE account_no=?",(rec,)); exists=cur.fetchone()
            if not sender: con.close(); messagebox.showerror("Error","Sender account not found"); return
            if not exists: con.close(); messagebox.showerror("Error","Receiver Account Not Found"); return
            if amt>sender[0]: con.close(); messagebox.showerror("Error","Insufficient Balance"); return
            cur.execute("UPDATE users SET balance=balance-? WHERE account_no=?",(amt,acc))
            cur.execute("UPDATE users SET balance=balance+? WHERE account_no=?",(amt,rec))
            transaction(acc,"Transfer Sent",amt,cur); transaction(rec,"Transfer Received",amt,cur)
            con.commit(); con.close(); messagebox.showinfo("Success","Money Transferred Successfully"); w.destroy()
        except ValueError: messagebox.showerror("Error","Enter valid transfer details")
        except sqlite3.Error as ex: messagebox.showerror("Database Error",str(ex))
    tk.Button(w,text="Transfer",width=15,height=2,command=send).pack(pady=20)

# ---------------- TRANSACTION HISTORY ----------------
def transaction_history(acc):
    w=window("Transaction History","700x420")
    frame=tk.Frame(w); frame.pack(fill="both",expand=True,padx=15,pady=15)
    cols=("id","type","amount","date")
    table=ttk.Treeview(frame,columns=cols,show="headings")
    heads=("ID","Transaction Type","Amount","Date & Time")
    widths=(60,180,120,230)
    for c,h,wd in zip(cols,heads,widths):
        table.heading(c,text=h); table.column(c,width=wd)
    sc=ttk.Scrollbar(frame,orient="vertical",command=table.yview)
    table.configure(yscrollcommand=sc.set); table.pack(side="left",fill="both",expand=True); sc.pack(side="right",fill="y")
    con=db(); cur=con.cursor()
    cur.execute("SELECT id,transaction_type,amount,date_time FROM transactions WHERE account_no=? ORDER BY id DESC",(acc,))
    rows=cur.fetchall(); con.close()
    for r in rows: table.insert("",tk.END,values=(r[0],r[1],f"₹{r[2]:.2f}",r[3]))
    if not rows: table.insert("",tk.END,values=("","No Transactions","",""))

# ---------------- DASHBOARD ----------------
def dashboard(acc):
    d=tk.Toplevel(root); d.title("Online Banking System"); d.geometry("700x700")
    d.configure(bg="#F5F9FF"); d.resizable(False,False)
    con=db(); cur=con.cursor(); cur.execute("SELECT account_holder_name FROM users WHERE account_no=?",(acc,))
    r=cur.fetchone(); con.close(); name=r[0] if r else "User"
    h=tk.Frame(d,bg="#003366"); h.pack(fill="x")
    tk.Label(h,text="🏦 ONLINE BANKING SYSTEM",font=("Segoe UI",22,"bold"),bg="#003366",fg="white").pack(pady=(10,0))
    tk.Label(h,text="Secure • Fast • Reliable Banking",font=("Segoe UI",10),bg="#003366",fg="white").pack()
    tk.Label(d,text=f"Welcome, {name}",font=("Segoe UI",20,"bold"),bg="#F5F9FF",fg="#003366").pack(pady=15)
    tk.Label(d,text=f"Account Number : {acc}",font=("Segoe UI",11),bg="#F5F9FF").pack(pady=(0,20))
    style={"width":25,"height":2,"font":("Segoe UI",11,"bold"),"bd":0,"cursor":"hand2"}
    buttons=[
        ("💳 Balance","#E3F2FD","#0D47A1",lambda:balance_enquiry(acc)),
        ("💰 Deposit","#E8F5E9","#1B5E20",lambda:deposit(acc)),
        ("💸 Withdraw","#FFEBEE","#B71C1C",lambda:withdraw(acc)),
        ("🔄 Transfer","#E0F7FA","#006064",lambda:transfer_money(acc)),
        ("📜 Transaction History","#F3E5F5","#6A1B9A",lambda:transaction_history(acc))]
    for txt,bg,fg,cmd in buttons:
        tk.Button(d,text=txt,bg=bg,fg=fg,command=cmd,**style).pack(pady=6)
    def logout():
        if messagebox.askyesno("Logout","Are you sure you want to logout?"):
            d.destroy(); root.deiconify()
    tk.Button(d,text="🚪 Logout",bg="#ECEFF1",fg="#37474F",command=logout,**style).pack(pady=20)
    tk.Label(d,text="© 2026 Online Banking System",bg="#003366",fg="white").pack(side="bottom",fill="x",pady=7)

# ---------------- CREATE ACCOUNT ----------------
def create_account():
    w=window("Create Account","500x720"); frame=tk.Frame(w,bg="#F5F9FF"); frame.pack(pady=10)
    fields=["Account Number","Account Holder Name","Username","Password","Opening Balance","Mobile Number","PAN Number","Aadhaar Number"]
    ent={}
    for i,f in enumerate(fields):
        tk.Label(frame,text=f,bg="#F5F9FF",font=("Arial",10,"bold")).grid(row=i,column=0,sticky="w",pady=6)
        e=tk.Entry(frame,width=30,show="*" if f=="Password" else ""); e.grid(row=i,column=1,padx=15); ent[f]=e
    tk.Label(frame,text="Address",bg="#F5F9FF",font=("Arial",10,"bold")).grid(row=8,column=0,sticky="nw",pady=6)
    address=tk.Text(frame,width=23,height=3); address.grid(row=8,column=1,padx=15)
    tk.Label(frame,text="Account Type",bg="#F5F9FF",font=("Arial",10,"bold")).grid(row=9,column=0,sticky="w",pady=6)
    typ=ttk.Combobox(frame,values=["Savings","Current","Salary"],width=27,state="readonly"); typ.set("Savings"); typ.grid(row=9,column=1,padx=15)
    def register():
        vals={f:ent[f].get().strip() for f in fields}
        addr=address.get("1.0",tk.END).strip(); at=typ.get()
        if not all(vals.values()) or not addr or not at:
            messagebox.showerror("Error","All fields are required"); return
        try: opening=float(vals["Opening Balance"]); assert opening>=0
        except: messagebox.showerror("Error","Opening Balance must be a valid number"); return
        if not vals["Mobile Number"].isdigit() or len(vals["Mobile Number"])!=10:
            messagebox.showerror("Error","Mobile Number must contain 10 digits"); return
        try:
            con=db(); cur=con.cursor()
            cur.execute("""INSERT INTO users(account_no,account_holder_name,username,password,
                opening_balance,balance,mobile,address,pan,aadhaar,account_type)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (vals["Account Number"],vals["Account Holder Name"],vals["Username"],vals["Password"],
                 opening,opening,vals["Mobile Number"],addr,vals["PAN Number"],vals["Aadhaar Number"],at))
            con.commit(); con.close(); messagebox.showinfo("Success","Account Created Successfully"); w.destroy()
        except sqlite3.IntegrityError: messagebox.showerror("Error","Account Number or Username Already Exists")
        except sqlite3.Error as ex: messagebox.showerror("Database Error",str(ex))
    tk.Button(w,text="Create Account",width=22,height=2,bg="#0A5EB0",fg="white",font=("Arial",11,"bold"),command=register).pack(pady=15)

# ---------------- LOGIN ----------------
def login():
    w=window("Login","450x350")
    tk.Label(w,text="Account Number",bg="#F5F9FF",font=("Arial",10,"bold")).pack(pady=(25,5))
    account=tk.Entry(w,width=30); account.pack()
    tk.Label(w,text="Password",bg="#F5F9FF",font=("Arial",10,"bold")).pack(pady=(15,5))
    password=tk.Entry(w,width=30,show="*"); password.pack()
    def check():
        acc=account.get().strip(); pwd=password.get().strip()
        if not acc or not pwd: messagebox.showerror("Error","Enter Account Number and Password"); return
        con=db(); cur=con.cursor()
        cur.execute("SELECT account_no FROM users WHERE account_no=? AND password=?",(acc,pwd))
        r=cur.fetchone(); con.close()
        if r:
            messagebox.showinfo("Success","Login Successful"); w.destroy(); root.withdraw(); dashboard(r[0])
        else: messagebox.showerror("Error","Invalid Account Number or Password")
    tk.Button(w,text="Login",bg="#0A5EB0",fg="white",font=("Arial",11,"bold"),width=20,height=2,bd=0,command=check).pack(pady=25)

# ---------------- CUSTOMER RECORDS ----------------
def show_customer_count():
    w=window("Customer Records","1050x520")
    con=db(); cur=con.cursor()
    cur.execute("""SELECT account_no,account_holder_name,mobile,account_type,
                   opening_balance,balance,address FROM users ORDER BY account_no""")
    rows=cur.fetchall(); con.close()
    tk.Label(w,text=f"Total Customers : {len(rows)}",font=("Segoe UI",14,"bold"),
             bg="#F5F9FF",fg="#003366").pack(pady=10)
    frame=tk.Frame(w); frame.pack(fill="both",expand=True,padx=12,pady=5)
    cols=("acc","name","mobile","type","opening","balance","address")
    table=ttk.Treeview(frame,columns=cols,show="headings")
    heads=["Account No.","Customer Name","Mobile","Account Type","Opening Balance","Current Balance","Address"]
    for c,h in zip(cols,heads): table.heading(c,text=h); table.column(c,width=130)
    table.column("address",width=220)
    ys=ttk.Scrollbar(frame,orient="vertical",command=table.yview)
    xs=ttk.Scrollbar(frame,orient="horizontal",command=table.xview)
    table.configure(yscrollcommand=ys.set,xscrollcommand=xs.set)
    table.pack(side="top",fill="both",expand=True); ys.pack(side="right",fill="y"); xs.pack(side="bottom",fill="x")
    for r in rows:
        table.insert("",tk.END,values=(r[0],r[1],r[2],r[3],f"₹{r[4]:.2f}",f"₹{r[5]:.2f}",r[6]))
    def details():
        s=table.selection()
        if not s: messagebox.showwarning("Select Customer","Please select a customer"); return
        v=table.item(s[0],"values")
        messagebox.showinfo("Customer Details",
            f"Account No. : {v[0]}\nName : {v[1]}\nMobile : {v[2]}\n"
            f"Account Type : {v[3]}\nOpening Balance : {v[4]}\n"
            f"Current Balance : {v[5]}\nAddress : {v[6]}")
    tk.Button(w,text="View Customer Details",width=25,height=2,bg="#0A5EB0",
              fg="white",font=("Segoe UI",11,"bold"),bd=0,command=details).pack(pady=10)

# ---------------- MAIN WINDOW ----------------
root=tk.Tk()
root.title("Online Banking System"); root.geometry("700x550")
root.configure(bg="#F5F9FF"); root.resizable(False,False)
header=tk.Frame(root,bg="#003366"); header.pack(fill="x")
tk.Label(header,text="🏦 ONLINE BANKING SYSTEM",font=("Segoe UI",24,"bold"),bg="#003366",fg="white").pack(pady=(15,0))
tk.Label(header,text="Secure • Fast • Reliable Banking",font=("Segoe UI",11),bg="#003366",fg="white").pack()
tk.Label(root,text="Welcome",font=("Segoe UI",22,"bold"),bg="#F5F9FF",fg="#003366").pack(pady=(35,5))
tk.Label(root,text="Please choose an option to continue",font=("Segoe UI",11),bg="#F5F9FF").pack(pady=(0,30))
main_btn={"bg":"#0A5EB0","fg":"white","font":("Segoe UI",11,"bold"),"width":22,"height":2,"bd":0,"cursor":"hand2"}
tk.Button(root,text="Create Account",command=create_account,**main_btn).pack(pady=20)
tk.Button(root,text="Login",command=login,**main_btn).pack(pady=10)
tk.Button(root,text="Customer Records",command=show_customer_count,**main_btn).pack(pady=10)
tk.Button(root,text="Exit",bg="#6C757D",fg="white",font=("Segoe UI",11,"bold"),width=22,height=2,bd=0,cursor="hand2",command=root.destroy).pack(pady=10)
root.mainloop()

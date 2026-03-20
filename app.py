from flask import Flask, render_template, request, jsonify, Response, redirect, url_for, flash
import csv
import io
import pyodbc

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    conn = pyodbc.connect(
        'Driver={SQL Server};' 
        'Server=;' 
        'DATABASE=;' 
        'Trusted_Connection=yes;'
    )
    return conn

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/index")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers ORDER BY PersonID ASC")
    customers = cursor.fetchall()
    conn.close()
    return render_template("index.html", customers = customers)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        PersonID = request.form["PersonID"]
        LastName = request.form["LastName"]
        FirstName = request.form["FirstName"]
        Address = request.form["Address"]
        City = request.form["City"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Customers (PersonID, LastName, FirstName, Address, City) VALUES (?, ?, ?, ?, ?)", (PersonID, FirstName, LastName, Address, City)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route('/delete/<int:PersonID>')
def delete(PersonID):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customers WHERE PersonID = ?", PersonID)
    conn.commit()
    conn.close()
    return redirect('/index')

@app.route("/update/<int:PersonID>", methods=["GET", "POST"])
def update(PersonID):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        LastName = request.form["LastName"]
        FirstName = request.form["FirstName"]
        Address = request.form["Address"]
        City = request.form["City"]

        cursor.execute("""UPDATE Customers
                SET LastName = ?, FirstName = ?, Address = ?, City = ?
                Where PersonID = ?""", (LastName, FirstName, Address, City, PersonID))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    
    cursor.execute("SELECT PersonID, LastName, FirstName, Address, City FROM Customers WHERE PersonID = ?", (PersonID,))
    customer = cursor.fetchone()
    conn.close()
    return render_template("update.html", customer = customer)

@app.route("/export")
def export():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT PersonID, LastName, FirstName, Address, City FROM Customers")
    customers = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["PersonID", "LastName", "FirstName", "Address", "City"])

    for c in customers:
        writer.writerow([c.PersonID, c.LastName, c.FirstName, c.Address, c.City])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=customers.csv"
    return response

@app.route("/import", methods=["POST"])
def import_csv():
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("No file selected")
        return redirect(url_for("index"))
    
    stream = io.TextIOWrapper(file.stream, encoding ="utf-8-sig", newline ="")
    reader = csv.DictReader(stream)

    conn = get_db_connection()
    cursor = conn.cursor()

    rows_added = 0
    for row in reader:
        print("DEBUG ROW:",row)
        cursor.execute("INSERT INTO Customers (PersonID, LastName, FirstName, Address, City) VALUES (?, ?, ?, ?, ?)",
                       (row["PersonID"], row["LastName"], row["FirstName"], row["Address"], row["City"]))
        rows_added += 1
        
    conn.commit()
    conn.close()
    flash(f"CSV imported succesfully {rows_added} rows added.")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug = True)

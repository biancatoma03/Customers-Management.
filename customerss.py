from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import pyodbc
import csv
import io

customerss = Flask(__name__)
customerss.debug = True

def connection():
    s = ''
    d = 'Customers'
    Trusted_Connection = 'yes'
    conn = pyodbc.connect(
    'Driver={SQL Server};' 
    'Server=;' 
    'DATABASE=;' 
    'Trusted_Connection=yes;'
    ''
)
    return conn    

@customerss.route("/")
def main():
    customers = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers ORDER BY PersonID ASC")
    for row in cursor.fetchall():
        customers.append({"PersonID": row[0], "LastName": row[1], "FirstName": row[2], "Address": row[3], "City": row[4]})
    conn.close()
    return render_template("CustomersList.html", customers = customers)

@customerss.route('/AddCustomer', methods=['GET','POST'])
def AddCustomer():
 if request.method == 'GET':
        return render_template('AddCustomer.html')
 if request.method == 'POST':
        try:
            data = request.form
            PersonID = data.get('PersonID')
            LastName = data.get('LastName')
            FirstName = data.get('FirstName')
            Address = data.get('Address')
            City = data.get('City')

            conn = connection()
            cursor = conn.cursor()
            query = "INSERT INTO Customers (PersonID, LastName, FirstName, Address, City) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (PersonID, LastName, FirstName, Address, City))
            conn.commit()
            conn.close()

            return redirect('/')
        except  Exception as e:
             return jsonify({"error": str(e)}), 500

@customerss.route('/updateCustomer/<int:PersonID>',methods = ['GET','POST'])
def updateCustomer(PersonID):
    conn = connection()
    cursor = conn.cursor()

    if request.method == 'GET':
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PersonID, LastName, FirstName, Address, City FROM Customers WHERE PersonID = ?", (PersonID,))
            row = cursor.fetchone()
            conn.close()
    
    if request.method == 'POST':
        try:
            LastName = request.form['LastName']
            FirstName= request.form['FirstName']
            Address  = request.form['Address']
            City     = request.form['City']

            cursor.execute("""  
                UPDATE Customers
                SET LastName = ?, FirstName = ?, Address = ?, City = ?
                Where PersonID = ?
            """, (LastName, FirstName, Address, City, PersonID))

            conn.commit()
            conn.close()
            return redirect(url_for('main'))
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500
        
    customer = {
        "PersonID": row[0],
        "LastName": row[1],
        "FirstName": row[2],
        "Address": row[3],
        "City": row[4]
    }
    return render_template("UpdateCustomer.html", customer = customer)
        
@customerss.route('/deleteCustomer/<int:PersonID>')
def deleteCustomer(PersonID):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customers WHERE PersonID = ?", PersonID)
    conn.commit()
    conn.close()
    return redirect('/')

def get_all_customers():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Customers')
    return cursor.fetchall()

def export_to_csv(data):
    with open('customers.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['id', 'Last Name', 'First Name', 'Address', 'City'])
        csv_writer.writerows(data)

@customerss.route('/exportCSV')
def exportCSV():
    customers = get_all_customers()
    export_to_csv(customers)
    return Response(open('customers.csv', 'r'), mimetype = 'text/csv', headers = {'Content-Disposition': 'attachmnt; filename=customers.csv'})

if __name__ == '__main__':
    customerss.run()
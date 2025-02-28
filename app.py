from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
import boto3

app = Flask(__name__)
CORS(app)

s3 = boto3.client('s3')
BUCKET_NAME='aws-project-virtualclassroom01'

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="database129.cpysuac0qjco.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="#database#",
            database="userdb"
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

@app.route("/", methods=["GET"])
def get_res():
    return "Works"

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user = data.get('user')
    name = data.get('name')
    gmail = data.get('gmail')
    phone_number = data.get('phone_number')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f'INSERT INTO {user} (name, email, phone_number, password) VALUES (%s, %s, %s, %s)'
        cursor.execute(query, (name, gmail, phone_number, password))
        conn.commit()
        response = jsonify({"message": "Signup successful!"})
        response.status_code = 200
    except mysql.connector.IntegrityError as e:
        response = jsonify({"message": "E-mail already exists with another user."})
        response.status_code = 409
    finally:
        cursor.close()
        conn.close()

    return response

@app.route("/getcourselist", methods=["GET"])
def getcourselist():
    res = s3.list_objects_v2(Bucket=BUCKET_NAME, Delimiter='/')
    folders = set()
    if "CommonPrefixes" in res:
        for p in res['CommonPrefixes']:
            folders.append(p['Prefix'])
    print(folders)
    return jsonify({"courses": list(folders)})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user1 = data.get('user')
    gmail = data.get("gmail")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = f'SELECT * FROM {user} WHERE email = %s AND password = %s'
    cursor.execute(query, (gmail, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful!"}), 200
    else:
        return jsonify({"message": "Invalid email or password."}), 401

if __name__ == "__main__":
    app.run(debug=True)
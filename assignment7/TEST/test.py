import psycopg2

def table():
    conn = psycopg2.connect(dbname="postgres",user="postgres",password="vansh123",host="localhost",port="5432")

    cursor = conn.cursor()
    cursor.execute('''create table employess(Name text, ID int, Age int);''')
    print("Table Created Sucsessfully")

    conn.commit()
    conn.close()

def execute():
    conn = psycopg2.connect(dbname="postgres",user="postgres",password="vansh123",host="localhost",port="5432")

    cursor = conn.cursor()
    cursor.execute('''select * from employess;''')
    show = cursor.fetchone()
    print(show)
    print(show[0])
    print(show[1])
    print(show[2])

    conn.commit()
    conn.close()

def data():
    conn = psycopg2.connect(dbname="postgres",user="postgres",password="vansh123",host="localhost",port="5432")
    cursor = conn.cursor()

    name=input("Enter Name : ")
    id=input("Enter ID : ")
    age=input("Enter Age : ")

    query='''insert into employess(Name , ID , Age) values(%s,%s,%s);'''

    cursor.execute(query,(name,id,age))
    print("Data Added Sucsessfully")

    conn.commit()
    conn.close()

data()
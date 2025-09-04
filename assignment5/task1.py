# Task 1: Create a Dictionary of Student Marks

dict = {
    "name":"Vansh",
}

s_name=input("Enter Student Name :")

if s_name==dict["name"]:
    marks=input(f"Enter {s_name}'s Marks :")
    dict["marks"]=marks
    print(dict)
else:
    print("Student Not Found")

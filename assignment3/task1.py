def factorial(n):
    if(n<2):
        return n
    else:
        return n * factorial(n-1)

a = int(input("Enter int Number : "))

print(f"Factorai of {a} is : ",factorial(a))
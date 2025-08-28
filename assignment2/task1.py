# Check if a Number is Even or Odd

num = int(input("Enter a number : "))

if(num<=0):
    print("Enter number greater than Zero ")
elif((num%2)==0):
    print(f"{num} is even number")
else:
    print(f"{num} is odd number")
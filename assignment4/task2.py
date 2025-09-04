

data = input("Enter some text to write into the file: ")

with open("output.txt", "w") as file:
    file.write(data + "\n")

print("Data written to output.txt successfully.")

append_data = input("Enter some text to append into the file: ")

with open("output.txt", "a") as file:
    file.write(append_data + "\n")

print("Data appended to output.txt successfully.")

print("\nFinal content of output.txt:")
with open("output.txt", "r") as file:
    content = file.read()
    print(content)

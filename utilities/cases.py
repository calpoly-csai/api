object1 = "myNumAndStringApplesAreCool42"
object = []
alreadyNum = True
for char in object1:  # for each character in the object
    if char.isupper():  # if the character is uppercase
        ascii = ord(char)
        ascii += 32
        object.append("_" + chr(ascii))
    elif char in "0123456789" and alreadyNum == True:
        alreadyNum = False
        object.append("_" + str(char))
    elif char in "0123456789" and alreadyNum == False:
        object.append(char)
    else:
        object.append(char)
print("".join(object))  # join the list

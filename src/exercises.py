from math import pi

"""Write a Python program to accept a filename from the user and print the extension of that. Go to the editor
Sample filename : abc.java
Output : java"""


def get_extension():

    file_name= input("Enter file name : ")
    splitted_name = file_name.split(".")
    print(splitted_name[1])

"""Write a Python program that accepts an integer (n) and computes the value of n+nn+nnn. Go to the editor
Sample value of n is 5
Expected Result : 615"""

def compute(number):

    string = f"{number}, {number}{number}, {number}{number}{number}"
    lst = string.split(',')
    total = 0
    for num in lst:
        total += int(num)

    print(total)

# compute(5)


""" Write a Python program to get the volume of a sphere with radius 6."""

def calculate_sphere(radius):
    V = 4 / 3 * pi * radius **3

    print(V)

# calculate_sphere(6)


""" Write a Python program to get the difference between a given 
number and 17, if the number is greater than 17 return double the absolute difference."""


def get_diff(number):

    diff = number - 17
    if diff > 0:
        diff = diff * 2
    else:
        diff = diff * -1

    print(diff)

# get_diff(8)


""" Write a Python program to find whether a given number (accept from the user)
 is even or odd, print out an appropriate message to the user."""


def even_or_odd():

    number = int(input("Enter number : "))
    if number % 2 == 0:
        print(f"Number {number} is an even number !")
    else:
        print(f"Number {number} is an odd number !")

# even_or_odd()


"""Write a Python program to count the number 4 in a given list."""


def count_4s(lst):

    count = 0
    for num in lst:
        if num == 4:
            count += 1

    print(count)

count_4s([1, 4, 5, 2, 78, 56, 44, 4, 3, 2, 4,])




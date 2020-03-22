"""
1-Using * and ** to pass arguments to a function
2-Using * and ** to capture arguments passed into a function
3-Using * to accept keyword-only arguments
4-Using * to capture items during tuple unpacking
5-Using * to unpack iterables into a list/tuple
6-Using ** to unpack dictionaries into other dictionaries
"""

""" 
ASTERISKS FOR UNPACKING INTO FUNCTION CALL"""

# --------------------------------------------------------------------------------
numbers = [2, 1, 3, 4, 7]
more_numbers = [*numbers, 11, 18]
print(*more_numbers, sep=', ')
# 2, 1, 3, 4, 7, 11, 18

# --------------------------------------------------------------------------------
fruits = ['lemon', 'pear', 'watermelon', 'tomato']
print(fruits[0], fruits[1], fruits[2], fruits[3])
print(*fruits)


# --------------------------------------------------------------------------------
def transpose_list(list_of_lists):
    return [
        list(row)
        for row in zip(*list_of_lists)]


transpose_list([[1, 4, 7], [2, 5, 8], [3, 6, 9]])

# --------------------------------------------------------------------------------

"""The ** operator allows us to take a dictionary of key-value pairs and 
unpack it into keyword arguments in a function call."""

date_info = {'year': "2020", 'month': "01", 'day': "01"}
filename = "{year}-{month}-{day}.txt".format(**date_info)
print(filename)
# '2020-01-01.txt'


# --------------------------------------------------------------------------------
'''multiple times *'''
fruits = ['lemon', 'pear', 'watermelon', 'tomato']
numbers = [2, 1, 3, 4, 7]
print(*numbers, *fruits)
# 2 1 3 4 7 lemon pear watermelon tomato


'''multiple times ** '''
date_info = {'year': "2020", 'month': "01", 'day': "01"}
track_info = {'artist': "Beethoven", 'title': 'Symphony No 5'}
filename = "{year}-{month}-{day}--{artist}-{title}.txt".format(**date_info, **track_info)
print(filename)
# 2020-01-01--Beethoven-Symphony No 5.txt

# --------------------------------------------------------------------------------
"""
ASTERISKS FOR PACKING ARGUMENTS GIVEN TO FUNCTION"""
from random import randint


def roll(*dice):
    return sum(randint(1, die) for die in dice)


print(roll(20))  # 8
print(roll(6, 6))  # 3
print(roll(6, 6, 6))  # 13


# --------------------------------------------------------------------------------
def tag(tag_name, **attributes):
    attribute_list = [f'{name}="{value}"' for name, value in attributes.items()]
    return f"<{tag_name} {' '.join(attribute_list)}>"


print(tag('img', height=20, width=40, src="face.jpg"))

# --------------------------------------------------------------------------------
"""POSITIONAL ARGUMENTS WITH KEYWORD-ONLY ARGUMENTS"""


def get_multiple(*keys, dictionary, default=None):
    return [dictionary.get(key, default) for key in keys]


fruits = {'lemon': 'yellow', 'orange': 'orange', 'tomato': 'red'}
print(get_multiple('lemon', 'tomato', 'squash', dictionary=fruits, default='unknown'))

# --------------------------------------------------------------------------------
"""KEYWORD-ONLY ARGUMENTS WITHOUT POSITIONAL ARGUMENTS"""


def with_previous(iterable, *, fillvalue=None):
    """Yield each iterable item along with the item before it."""
    previous = fillvalue
    for item in iterable:
        yield previous, item
        previous = item


print(
    list(with_previous([2, 1, 3], fillvalue=0)))

# --------------------------------------------------------------------------------
"""ASTERISKS IN TUPLE UNPACKING"""

fruits = ['lemon', 'pear', 'watermelon', 'tomato']
first, second, *remaining = fruits
print(remaining)  # ['watermelon', 'tomato']
first, *remaining = fruits
print(remaining)  # ['pear', 'watermelon', 'tomato']
first, *middle, last = fruits
print(middle)  # ['pear', 'watermelon']

((first_letter, *remaining), *other_fruits) = fruits

# --------------------------------------------------------------------------------
"""ASTERISKS IN LIST LITERALS"""


def palindromify(sequence):
    return list(sequence) + list(reversed(sequence))


def palindromify(sequence):
    return [*sequence, *reversed(sequence)]


def rotate_first_item(sequence):
    return [*sequence[1:], sequence[0]]


# this isnt just limited to creating lists either.
fruits = ['lemon', 'pear', 'watermelon', 'tomato']
uppercase_fruits = (f.upper() for f in fruits)
print({*fruits, *uppercase_fruits})
# {'lemon', 'watermelon', 'TOMATO', 'LEMON', 'PEAR', 'WATERMELON', 'tomato', 'pear'}
# another way of doing this :
print(set().union(fruits, uppercase_fruits))
# {'lemon', 'watermelon', 'TOMATO', 'LEMON', 'PEAR', 'WATERMELON', 'tomato', 'pear'}

# --------------------------------------------------------------------------------

"""DOUBLE ASTERISKS IN DICTIONARY LITERALS"""
date_info = {'year': "2020", 'month': "01", 'day': "01"}
track_info = {'artist': "Beethoven", 'title': 'Symphony No 5'}
all_info = {**date_info, **track_info}
all_info

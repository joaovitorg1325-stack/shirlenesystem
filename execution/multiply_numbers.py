import sys
import argparse

def multiply_numbers(a, b):
    return a * b

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Multiply two numbers.')
    parser.add_argument('number1', type=float, help='The first number')
    parser.add_argument('number2', type=float, help='The second number')

    args = parser.parse_args()

    result = multiply_numbers(args.number1, args.number2)
    print(f"Result: {result}")

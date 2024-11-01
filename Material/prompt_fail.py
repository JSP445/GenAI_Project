class RPNCalculator:
    def __init__(self):
        self.operators = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide,
            '%': self.modulus
        }

    def add(self, x, y):
        return x + y

    def subtract(self, x, y):
        return x - y

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            return "Error: Division by zero"
        return x / y

    def modulus(self, x, y):
        return x % y

    def calculate(self, operator, operand1, operand2):
        if operator in self.operators:
            return self.operators[operator](operand1, operand2)
        else:
            return "Error: Unsupported operator"

    def run(self):
        print("Reverse Polish Notation Calculator")
        print("Enter in the format: operator operand1 operand2 (e.g., + 4 5)")
        print("Available operators: +, -, *, /, %")
        print("Type 'exit' to quit the program.")
        
        while True:
            user_input = input("Enter command: ")
            if user_input.lower() == "exit":
                print("Exiting the calculator. Goodbye!")
                break
            
            try:
                operator, operand1, operand2 = user_input.split()
                operand1, operand2 = float(operand1), float(operand2)
                result = self.calculate(operator, operand1, operand2)
                print(f"Result: {result}")
            except ValueError:
                print("Error: Invalid input format. Please enter in the format: operator operand1 operand2")
            except Exception as e:
                print(f"An error occurred: {e}")


# Run the RPN calculator
if __name__ == "__main__":
    calculator = RPNCalculator()
    calculator.run()

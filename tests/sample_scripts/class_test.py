class Student:
    school = "ABC School"

    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.year = 2026

    def get_details(self):
        result = self.name
        return result


student = Student("Chandana", 21)
message = student.get_details()

print(message)
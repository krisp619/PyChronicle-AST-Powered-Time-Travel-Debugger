import ast

from ast_variable_parser import VariableAssignmentVisitor


def test_parser(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        source = file.read()

    tree = ast.parse(source)

    visitor = VariableAssignmentVisitor()
    visitor.visit(tree)

    for assignment in visitor.assignments:
        print(assignment)


test_parser("tests/sample_scripts/class_test.py")
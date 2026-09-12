"""
PyChronicle - Week 1 - Member 1 (Pair A: Core Engineering)
-----------------------------------------------------------
Task: Parse a target Python file's Abstract Syntax Tree (AST)
and identify all variable assignments.

This is the foundation for the whole PyChronicle project:
- Member 2 will test this against tricky scripts (loops, functions, classes)
- Member 3's SQLite schema expects: line_number, variable_name
- Week 2's tracer (sys.settrace) will use this to know WHICH lines to watch

Usage:
    python ast_variable_parser.py path/to/target_script.py
"""

import ast
import sys
from dataclasses import dataclass, field


@dataclass
class Assignment:
    line_number: int
    variable_names: list       # list because "a, b = 1, 2" assigns two names at once
    assignment_type: str       # "Assign" | "AugAssign" | "AnnAssign" | "For" | "With"
    source_snippet: str        # human-readable representation of the RHS / statement


class VariableAssignmentVisitor(ast.NodeVisitor):
    """
    Walks the AST and records every place a variable is assigned a value.
    """

    def __init__(self):
        self.assignments: list[Assignment] = []

    # --- helper -----------------------------------------------------
    def _extract_names(self, target) -> list[str]:
        """
        A target can be a simple Name (x), a Tuple/List (a, b), or an
        Attribute/Subscript (obj.attr, arr[0]) which we also capture
        by their unparsed text so nothing is silently dropped.
        """
        names = []
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                names.extend(self._extract_names(elt))
        else:
            # Attribute (self.x), Subscript (arr[0]), Starred (*rest), etc.
            try:
                names.append(ast.unparse(target))
            except Exception:
                names.append(type(target).__name__)
        return names

    # --- standard assignment: x = 5 ----------------------------------
    def visit_Assign(self, node: ast.Assign):
        names = []
        for target in node.targets:
            names.extend(self._extract_names(target))
        self.assignments.append(Assignment(
            line_number=node.lineno,
            variable_names=names,
            assignment_type="Assign",
            source_snippet=ast.unparse(node),
        ))
        self.generic_visit(node)

    # --- augmented assignment: x += 5 ---------------------------------
    def visit_AugAssign(self, node: ast.AugAssign):
        names = self._extract_names(node.target)
        self.assignments.append(Assignment(
            line_number=node.lineno,
            variable_names=names,
            assignment_type="AugAssign",
            source_snippet=ast.unparse(node),
        ))
        self.generic_visit(node)

    # --- annotated assignment: x: int = 5 -----------------------------
    def visit_AnnAssign(self, node: ast.AnnAssign):
        names = self._extract_names(node.target)
        self.assignments.append(Assignment(
            line_number=node.lineno,
            variable_names=names,
            assignment_type="AnnAssign",
            source_snippet=ast.unparse(node),
        ))
        self.generic_visit(node)

    # --- for-loop target: for i in range(10): -------------------------
    def visit_For(self, node: ast.For):
        names = self._extract_names(node.target)
        self.assignments.append(Assignment(
            line_number=node.lineno,
            variable_names=names,
            assignment_type="For",
            source_snippet=f"for {ast.unparse(node.target)} in {ast.unparse(node.iter)}:",
        ))
        self.generic_visit(node)

    # --- with-as target: with open(f) as fh: ---------------------------
    def visit_With(self, node: ast.With):
        for item in node.items:
            if item.optional_vars is not None:
                names = self._extract_names(item.optional_vars)
                self.assignments.append(Assignment(
                    line_number=node.lineno,
                    variable_names=names,
                    assignment_type="With",
                    source_snippet=ast.unparse(node).splitlines()[0],
                ))
        self.generic_visit(node)


def parse_file(filepath: str) -> list[Assignment]:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source, filename=filepath)
    visitor = VariableAssignmentVisitor()
    visitor.visit(tree)

    # Sort by line number so output reads top-to-bottom like the source file
    return sorted(visitor.assignments, key=lambda a: a.line_number)


def main():
    if len(sys.argv) != 2:
        print("Usage: python ast_variable_parser.py <target_script.py>")
        sys.exit(1)

    target = sys.argv[1]
    assignments = parse_file(target)

    print(f"\nFound {len(assignments)} variable assignment(s) in {target}:\n")
    print(f"{'Line':<6} {'Type':<10} {'Variable(s)':<20} Source")
    print("-" * 70)
    for a in assignments:
        vars_str = ", ".join(a.variable_names)
        print(f"{a.line_number:<6} {a.assignment_type:<10} {vars_str:<20} {a.source_snippet}")


if __name__ == "__main__":
    main()

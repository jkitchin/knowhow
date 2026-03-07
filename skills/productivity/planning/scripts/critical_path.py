#!/usr/bin/env python3
"""
Critical Path Method (CPM) Calculator

Calculates the critical path for a project given tasks, durations, and dependencies.
Uses forward pass (early start/finish) and backward pass (late start/finish) to
identify the critical path and calculate float/slack for each task.

Usage:
    python critical_path.py <tasks_file.json>
    python critical_path.py <tasks_file.json> --output <output.json>
    python critical_path.py --example

Input JSON Format:
{
  "tasks": [
    {
      "id": "A",
      "name": "Task name",
      "duration": 5,
      "dependencies": []
    },
    {
      "id": "B",
      "name": "Another task",
      "duration": 3,
      "dependencies": ["A"]
    }
  ]
}

Output:
- Critical path (sequence of tasks with zero float)
- Project duration
- Task details with early/late start/finish and float
- Gantt-style visualization

Example:
    # Create example input file
    python critical_path.py --example > tasks.json

    # Calculate critical path
    python critical_path.py tasks.json

    # Save results to JSON
    python critical_path.py tasks.json --output results.json
"""

import json
import sys


class Task:
    """Represents a project task with CPM calculations."""

    def __init__(self, task_id: str, name: str, duration: int, dependencies: list[str]):
        self.id = task_id
        self.name = name
        self.duration = duration
        self.dependencies = dependencies

        # CPM calculations
        self.early_start = 0
        self.early_finish = 0
        self.late_start = 0
        self.late_finish = 0
        self.float = 0
        self.is_critical = False

    def calculate_early_times(self, tasks_dict: dict[str, "Task"]):
        """Calculate early start and early finish (forward pass)."""
        if not self.dependencies:
            self.early_start = 0
        else:
            # Early start is the maximum early finish of all dependencies
            self.early_start = max(tasks_dict[dep_id].early_finish for dep_id in self.dependencies)

        self.early_finish = self.early_start + self.duration

    def calculate_late_times(self, tasks_dict: dict[str, "Task"], project_duration: int):
        """Calculate late start and late finish (backward pass)."""
        # Find all tasks that depend on this one
        dependents = [task for task in tasks_dict.values() if self.id in task.dependencies]

        if not dependents:
            # This is an end task
            self.late_finish = project_duration
        else:
            # Late finish is minimum late start of all dependent tasks
            self.late_finish = min(task.late_start for task in dependents)

        self.late_start = self.late_finish - self.duration

    def calculate_float(self):
        """Calculate float (slack) and determine if task is critical."""
        self.float = self.late_start - self.early_start
        # Alternative: self.float = self.late_finish - self.early_finish
        self.is_critical = self.float == 0

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON output."""
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "dependencies": self.dependencies,
            "early_start": self.early_start,
            "early_finish": self.early_finish,
            "late_start": self.late_start,
            "late_finish": self.late_finish,
            "float": self.float,
            "is_critical": self.is_critical,
        }


def validate_tasks(tasks_data: list[dict]) -> list[str]:
    """Validate task data and return list of errors."""
    errors = []
    task_ids = {task["id"] for task in tasks_data}

    for task in tasks_data:
        # Check required fields
        if "id" not in task:
            errors.append("Task missing 'id' field")
            continue

        if "duration" not in task:
            errors.append(f"Task {task['id']} missing 'duration' field")
        elif task["duration"] <= 0:
            errors.append(f"Task {task['id']} has non-positive duration")

        # Check dependencies exist
        if "dependencies" in task:
            for dep in task["dependencies"]:
                if dep not in task_ids:
                    errors.append(f"Task {task['id']} depends on non-existent task {dep}")

    # Check for circular dependencies
    if not errors:
        circular = find_circular_dependencies(tasks_data)
        if circular:
            errors.append(f"Circular dependency detected: {' → '.join(circular)}")

    return errors


def find_circular_dependencies(tasks_data: list[dict]) -> list[str]:
    """Detect circular dependencies using depth-first search."""
    # Build adjacency list
    graph = {task["id"]: task.get("dependencies", []) for task in tasks_data}

    visited = set()
    rec_stack = set()

    def has_cycle(node: str, path: list[str]) -> list[str]:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = has_cycle(neighbor, path.copy())
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]

        rec_stack.remove(node)
        return []

    for task_id in graph:
        if task_id not in visited:
            cycle = has_cycle(task_id, [])
            if cycle:
                return cycle

    return []


def topological_sort(tasks: dict[str, Task]) -> list[str]:
    """
    Return tasks in topological order (dependencies before dependents).
    Uses Kahn's algorithm.
    """
    # Count incoming edges for each task
    in_degree = {task_id: 0 for task_id in tasks}
    for task in tasks.values():
        for dep in task.dependencies:
            in_degree[task.id] += 1

    # Queue of tasks with no dependencies
    queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
    sorted_tasks = []

    while queue:
        # Remove task with no dependencies
        task_id = queue.pop(0)
        sorted_tasks.append(task_id)

        # Find tasks that depend on this one
        for other_task in tasks.values():
            if task_id in other_task.dependencies:
                in_degree[other_task.id] -= 1
                if in_degree[other_task.id] == 0:
                    queue.append(other_task.id)

    return sorted_tasks


def calculate_critical_path(tasks_data: list[dict]) -> tuple[dict[str, Task], list[str], int]:
    """
    Calculate critical path for given tasks.

    Returns:
        Tuple of (tasks_dict, critical_path, project_duration)
    """
    # Validate input
    errors = validate_tasks(tasks_data)
    if errors:
        raise ValueError("Invalid task data:\n" + "\n".join(errors))

    # Create Task objects
    tasks = {
        task_data["id"]: Task(
            task_data["id"],
            task_data.get("name", task_data["id"]),
            task_data["duration"],
            task_data.get("dependencies", []),
        )
        for task_data in tasks_data
    }

    # Sort tasks in dependency order
    task_order = topological_sort(tasks)

    # Forward pass: Calculate early start and early finish
    for task_id in task_order:
        tasks[task_id].calculate_early_times(tasks)

    # Project duration is the maximum early finish
    project_duration = max(task.early_finish for task in tasks.values())

    # Backward pass: Calculate late start and late finish
    for task_id in reversed(task_order):
        tasks[task_id].calculate_late_times(tasks, project_duration)

    # Calculate float and identify critical tasks
    for task in tasks.values():
        task.calculate_float()

    # Build critical path by following critical tasks
    critical_path = build_critical_path(tasks)

    return tasks, critical_path, project_duration


def build_critical_path(tasks: dict[str, Task]) -> list[str]:
    """
    Build the critical path by tracing critical tasks from start to finish.
    """
    critical_tasks = {task_id: task for task_id, task in tasks.items() if task.is_critical}

    if not critical_tasks:
        return []

    # Find start task(s) - critical tasks with no dependencies or only non-critical dependencies
    start_tasks = [
        task_id
        for task_id, task in critical_tasks.items()
        if not task.dependencies or all(dep not in critical_tasks for dep in task.dependencies)
    ]

    if not start_tasks:
        # Shouldn't happen with valid data, but handle gracefully
        return list(critical_tasks.keys())

    # Trace path from start to finish
    path = []
    current = start_tasks[0]
    visited = set()

    while current and current not in visited:
        path.append(current)
        visited.add(current)

        # Find next critical task that depends on current
        next_tasks = [
            task_id
            for task_id, task in critical_tasks.items()
            if current in task.dependencies and task_id not in visited
        ]

        current = next_tasks[0] if next_tasks else None

    return path


def print_results(tasks: dict[str, Task], critical_path: list[str], project_duration: int):
    """Print critical path analysis results to console."""
    print("\n" + "=" * 80)
    print("CRITICAL PATH METHOD (CPM) ANALYSIS")
    print("=" * 80)

    print(f"\nProject Duration: {project_duration} days")
    print(f"Critical Path: {' → '.join(critical_path)}")
    print(f"Number of Tasks: {len(tasks)}")
    print(f"Critical Tasks: {sum(1 for t in tasks.values() if t.is_critical)}")

    print("\n" + "-" * 80)
    print("TASK DETAILS")
    print("-" * 80)
    print(
        f"{'ID':<6} {'Name':<20} {'Dur':<5} {'ES':<5} {'EF':<5} "
        f"{'LS':<5} {'LF':<5} {'Float':<7} {'Critical':<10}"
    )
    print("-" * 80)

    # Sort by early start for readability
    sorted_tasks = sorted(tasks.values(), key=lambda t: t.early_start)

    for task in sorted_tasks:
        critical_mark = "✓ CRITICAL" if task.is_critical else ""
        print(
            f"{task.id:<6} {task.name:<20} {task.duration:<5} "
            f"{task.early_start:<5} {task.early_finish:<5} "
            f"{task.late_start:<5} {task.late_finish:<5} "
            f"{task.float:<7} {critical_mark:<10}"
        )

    print("\n" + "-" * 80)
    print("GANTT-STYLE TIMELINE")
    print("-" * 80)

    # Create simple ASCII timeline
    max_time = project_duration
    scale = max(1, max_time // 60)  # Scale for readability

    for task in sorted_tasks:
        bar_start = task.early_start // scale
        bar_length = max(1, task.duration // scale)
        critical_char = "█" if task.is_critical else "▒"

        timeline = " " * bar_start + critical_char * bar_length
        print(f"{task.id:<6} |{timeline}")

    # Print time scale
    print(f"{'Time':<6} |" + "".join(str(i % 10) for i in range(0, max_time, scale)))

    print("\n" + "=" * 80)
    print("LEGEND")
    print("=" * 80)
    print("ES = Early Start    | Earliest a task can start")
    print("EF = Early Finish   | Earliest a task can finish (ES + Duration)")
    print("LS = Late Start     | Latest a task can start without delaying project")
    print("LF = Late Finish    | Latest a task can finish without delaying project")
    print("Float = Slack       | How long a task can be delayed (LS - ES)")
    print("Critical = ✓        | Tasks with zero float (critical path)")
    print("█ = Critical task   | ▒ = Non-critical task")
    print("=" * 80 + "\n")


def save_results(
    tasks: dict[str, Task], critical_path: list[str], project_duration: int, output_file: str
):
    """Save results to JSON file."""
    results = {
        "project_duration": project_duration,
        "critical_path": critical_path,
        "tasks": [task.to_dict() for task in tasks.values()],
    }

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")


def print_example():
    """Print example input JSON."""
    example = {
        "tasks": [
            {"id": "A", "name": "Design wireframes", "duration": 5, "dependencies": []},
            {"id": "B", "name": "Client approval", "duration": 2, "dependencies": ["A"]},
            {"id": "C", "name": "Create visual designs", "duration": 7, "dependencies": ["B"]},
            {"id": "D", "name": "Develop frontend", "duration": 10, "dependencies": ["C"]},
            {"id": "E", "name": "Develop backend", "duration": 8, "dependencies": ["C"]},
            {"id": "F", "name": "Integration testing", "duration": 3, "dependencies": ["D", "E"]},
            {"id": "G", "name": "User acceptance testing", "duration": 4, "dependencies": ["F"]},
            {"id": "H", "name": "Deploy to production", "duration": 1, "dependencies": ["G"]},
        ]
    }

    print(json.dumps(example, indent=2))


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python critical_path.py <tasks_file.json>")
        print("       python critical_path.py --example")
        print("\nFor help: python critical_path.py --help")
        sys.exit(1)

    if sys.argv[1] in ["--help", "-h", "help"]:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] in ["--example", "-e", "example"]:
        print_example()
        sys.exit(0)

    # Load tasks from file
    input_file = sys.argv[1]
    try:
        with open(input_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{input_file}': {e}")
        sys.exit(1)

    if "tasks" not in data:
        print("Error: JSON must contain 'tasks' array")
        sys.exit(1)

    # Calculate critical path
    try:
        tasks, critical_path, project_duration = calculate_critical_path(data["tasks"])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Print results
    print_results(tasks, critical_path, project_duration)

    # Save to output file if specified
    if len(sys.argv) > 3 and sys.argv[2] in ["--output", "-o"]:
        save_results(tasks, critical_path, project_duration, sys.argv[3])


if __name__ == "__main__":
    main()

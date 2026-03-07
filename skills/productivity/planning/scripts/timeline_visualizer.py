#!/usr/bin/env python3
"""
Timeline Visualizer

Creates visual timeline representations (ASCII/Markdown) for project schedules.
Shows tasks, durations, dependencies, milestones, and parallel work.

Usage:
    python timeline_visualizer.py <timeline_file.json>
    python timeline_visualizer.py <timeline_file.json> --style gantt
    python timeline_visualizer.py <timeline_file.json> --style roadmap
    python timeline_visualizer.py --example

Input JSON Format:
{
  "project": "Project Name",
  "start_date": "2024-01-01",
  "tasks": [
    {
      "id": "T1",
      "name": "Task name",
      "start": "2024-01-01",
      "end": "2024-01-15",
      "owner": "John",
      "phase": "Planning"
    }
  ],
  "milestones": [
    {
      "name": "Milestone name",
      "date": "2024-01-15"
    }
  ]
}

Styles:
    - gantt: Traditional Gantt chart view (default)
    - roadmap: High-level roadmap view by phases
    - calendar: Month-by-month calendar view

Example:
    python timeline_visualizer.py --example > timeline.json
    python timeline_visualizer.py timeline.json
    python timeline_visualizer.py timeline.json --style roadmap
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta


class TimelineTask:
    """Represents a task on the timeline."""

    def __init__(
        self,
        task_id: str,
        name: str,
        start: datetime,
        end: datetime,
        owner: str = "",
        phase: str = "",
        status: str = "",
    ):
        self.id = task_id
        self.name = name
        self.start = start
        self.end = end
        self.owner = owner
        self.phase = phase
        self.status = status
        self.duration = (end - start).days + 1

    def overlaps_with(self, other: "TimelineTask") -> bool:
        """Check if this task overlaps with another task."""
        return not (self.end < other.start or self.start > other.end)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.strftime("%Y-%m-%d"),
            "end": self.end.strftime("%Y-%m-%d"),
            "duration": self.duration,
            "owner": self.owner,
            "phase": self.phase,
            "status": self.status,
        }


class Milestone:
    """Represents a project milestone."""

    def __init__(self, name: str, date: datetime, description: str = ""):
        self.name = name
        self.date = date
        self.description = description


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%B %d, %Y",
        "%b %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")


def load_timeline(
    data: dict,
) -> tuple[str, list[TimelineTask], list[Milestone], datetime, datetime]:
    """
    Load timeline from JSON data.

    Returns:
        Tuple of (project_name, tasks, milestones, start_date, end_date)
    """
    project_name = data.get("project", "Project Timeline")

    # Parse tasks
    tasks = []
    for task_data in data.get("tasks", []):
        task = TimelineTask(
            task_id=task_data["id"],
            name=task_data["name"],
            start=parse_date(task_data["start"]),
            end=parse_date(task_data["end"]),
            owner=task_data.get("owner", ""),
            phase=task_data.get("phase", ""),
            status=task_data.get("status", ""),
        )
        tasks.append(task)

    # Parse milestones
    milestones = []
    for ms_data in data.get("milestones", []):
        milestone = Milestone(
            name=ms_data["name"],
            date=parse_date(ms_data["date"]),
            description=ms_data.get("description", ""),
        )
        milestones.append(milestone)

    # Determine overall timeline
    if tasks:
        start_date = min(task.start for task in tasks)
        end_date = max(task.end for task in tasks)
    elif "start_date" in data:
        start_date = parse_date(data["start_date"])
        end_date = parse_date(data.get("end_date", data["start_date"]))
    else:
        start_date = datetime.now()
        end_date = start_date

    return project_name, tasks, milestones, start_date, end_date


def render_gantt_chart(
    project_name: str,
    tasks: list[TimelineTask],
    milestones: list[Milestone],
    start_date: datetime,
    end_date: datetime,
) -> str:
    """Render traditional Gantt chart."""
    output = []

    # Header
    output.append("=" * 80)
    output.append(f"GANTT CHART: {project_name}")
    output.append("=" * 80)

    total_days = (end_date - start_date).days + 1
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    output.append(f"\nTimeline: {start_str} to {end_str} ({total_days} days)")
    output.append(f"Tasks: {len(tasks)} | Milestones: {len(milestones)}")

    # Determine time scale
    if total_days <= 60:
        # Day-level granularity
        scale_unit = "day"
        scale_factor = 1
    elif total_days <= 180:
        # Week-level granularity
        scale_unit = "week"
        scale_factor = 7
    else:
        # Month-level granularity
        scale_unit = "month"
        scale_factor = 30

    timeline_width = max(60, min(100, total_days // scale_factor))

    # Time scale header
    output.append("\n" + "-" * 80)
    output.append("TIMELINE")
    output.append("-" * 80)

    # Create time markers
    current_date = start_date
    markers = []

    if scale_unit == "day":
        # Show every N days
        step = max(1, total_days // 50)
        while current_date <= end_date:
            pos = (current_date - start_date).days
            markers.append((pos, current_date.strftime("%m/%d")))
            current_date += timedelta(days=step)
    elif scale_unit == "week":
        # Show weeks
        while current_date <= end_date:
            pos = (current_date - start_date).days // scale_factor
            markers.append((pos, f"W{current_date.isocalendar()[1]}"))
            current_date += timedelta(weeks=1)
    else:
        # Show months
        while current_date <= end_date:
            pos = (current_date - start_date).days // scale_factor
            markers.append((pos, current_date.strftime("%b")))
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

    # Task name column width
    max_name_len = max(len(task.name) for task in tasks) if tasks else 20
    name_width = min(30, max(15, max_name_len))

    # Print header with time markers
    header_line = " " * (name_width + 2) + "|"
    for pos, label in markers:
        # Place marker at approximate position
        scaled_pos = min(
            timeline_width - len(label), pos * timeline_width // (total_days // scale_factor)
        )
        header_line += " " * (scaled_pos - len(header_line) + name_width + 3) + label

    output.append(header_line)
    output.append(" " * (name_width + 2) + "|" + "-" * timeline_width)

    # Render each task
    for task in sorted(tasks, key=lambda t: t.start):
        # Calculate bar position and length
        start_pos = int((task.start - start_date).days * timeline_width / total_days)
        end_pos = int((task.end - start_date).days * timeline_width / total_days)
        bar_length = max(1, end_pos - start_pos)

        # Choose bar character based on status
        if task.status.lower() in ["complete", "completed", "done"]:
            bar_char = "█"
        elif task.status.lower() in ["in progress", "in_progress", "active"]:
            bar_char = "▓"
        else:
            bar_char = "░"

        # Build bar
        bar = " " * start_pos + bar_char * bar_length

        # Task name with truncation
        task_name = task.name[:name_width].ljust(name_width)

        # Add owner/phase info
        info = ""
        if task.owner:
            info = f" ({task.owner[:10]})"
        elif task.phase:
            info = f" [{task.phase[:10]}]"

        output.append(f"{task_name}{info:12} |{bar}")

    # Add milestones
    if milestones:
        output.append(" " * (name_width + 2) + "|" + "-" * timeline_width)
        output.append(f"{'MILESTONES'.ljust(name_width + 12)} |")

        for ms in sorted(milestones, key=lambda m: m.date):
            ms_pos = int((ms.date - start_date).days * timeline_width / total_days)
            marker_line = " " * ms_pos + "▼"
            ms_name = ms.name[:name_width].ljust(name_width)
            ms_date = ms.date.strftime("%Y-%m-%d")
            output.append(f"{ms_name} {ms_date} |{marker_line}")

    # Legend
    output.append("\n" + "-" * 80)
    output.append("LEGEND")
    output.append("-" * 80)
    output.append("█ = Completed  ▓ = In Progress  ░ = Not Started  ▼ = Milestone")
    output.append("=" * 80 + "\n")

    return "\n".join(output)


def render_roadmap(
    project_name: str,
    tasks: list[TimelineTask],
    milestones: list[Milestone],
    start_date: datetime,
    end_date: datetime,
) -> str:
    """Render high-level roadmap grouped by phases."""
    output = []

    # Header
    output.append("=" * 80)
    output.append(f"PROJECT ROADMAP: {project_name}")
    output.append("=" * 80)

    total_days = (end_date - start_date).days + 1
    output.append(
        f"\n{start_date.strftime('%B %Y')} → {end_date.strftime('%B %Y')} ({total_days} days)"
    )

    # Group tasks by phase
    phases = defaultdict(list)
    for task in tasks:
        phase = task.phase if task.phase else "General"
        phases[phase].append(task)

    # Calculate phase timelines
    phase_info = {}
    for phase, phase_tasks in phases.items():
        phase_start = min(t.start for t in phase_tasks)
        phase_end = max(t.end for t in phase_tasks)
        phase_duration = (phase_end - phase_start).days + 1
        phase_info[phase] = (phase_start, phase_end, phase_duration, phase_tasks)

    # Sort phases by start date
    sorted_phases = sorted(phase_info.items(), key=lambda x: x[1][0])

    # Render each phase
    for phase, (phase_start, phase_end, phase_duration, phase_tasks) in sorted_phases:
        output.append("\n" + "-" * 80)
        output.append(f"Phase: {phase}")
        ps = phase_start.strftime("%Y-%m-%d")
        pe = phase_end.strftime("%Y-%m-%d")
        output.append(f"  Duration: {ps} to {pe} ({phase_duration} days)")
        output.append(f"  Tasks: {len(phase_tasks)}")

        # Calculate phase bar
        start_pos = int((phase_start - start_date).days * 60 / total_days)
        end_pos = int((phase_end - start_date).days * 60 / total_days)
        bar_length = max(1, end_pos - start_pos)

        bar = " " * start_pos + "█" * bar_length
        output.append(f"  {bar}")

        # List key tasks
        output.append("\n  Key Tasks:")
        for task in sorted(phase_tasks, key=lambda t: t.start)[:5]:  # Show first 5
            duration_str = f"{task.duration}d"
            owner_str = f" - {task.owner}" if task.owner else ""
            output.append(f"    • {task.name} ({duration_str}){owner_str}")

        if len(phase_tasks) > 5:
            output.append(f"    • ... and {len(phase_tasks) - 5} more tasks")

    # Add milestones
    if milestones:
        output.append("\n" + "-" * 80)
        output.append("MILESTONES")
        output.append("-" * 80)

        for ms in sorted(milestones, key=lambda m: m.date):
            ms_pos = int((ms.date - start_date).days * 60 / total_days)
            marker = " " * ms_pos + "▼"
            date_str = ms.date.strftime("%b %d, %Y")
            output.append(f"{date_str:15} {marker}  {ms.name}")
            if ms.description:
                output.append(f"                   {ms.description}")

    output.append("\n" + "=" * 80 + "\n")

    return "\n".join(output)


def render_calendar(
    project_name: str,
    tasks: list[TimelineTask],
    milestones: list[Milestone],
    start_date: datetime,
    end_date: datetime,
) -> str:
    """Render month-by-month calendar view."""
    output = []

    # Header
    output.append("=" * 80)
    output.append(f"CALENDAR VIEW: {project_name}")
    output.append("=" * 80)

    # Group tasks and milestones by month
    current = start_date.replace(day=1)
    end_month = end_date.replace(day=1)

    while current <= end_month:
        month_start = current
        # Get last day of month
        if current.month == 12:
            month_end = current.replace(year=current.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = current.replace(month=current.month + 1, day=1) - timedelta(days=1)

        # Filter tasks for this month
        month_tasks = [t for t in tasks if not (t.end < month_start or t.start > month_end)]

        # Filter milestones for this month
        month_milestones = [m for m in milestones if month_start <= m.date <= month_end]

        if month_tasks or month_milestones:
            output.append("\n" + "-" * 80)
            output.append(f"{current.strftime('%B %Y')}")
            output.append("-" * 80)

            if month_tasks:
                output.append(f"\nTasks ({len(month_tasks)}):")
                for task in sorted(month_tasks, key=lambda t: t.start):
                    start_str = task.start.strftime("%m/%d")
                    end_str = task.end.strftime("%m/%d")
                    owner_str = f" - {task.owner}" if task.owner else ""
                    output.append(f"  {start_str} → {end_str}  {task.name}{owner_str}")

            if month_milestones:
                output.append(f"\nMilestones ({len(month_milestones)}):")
                for ms in sorted(month_milestones, key=lambda m: m.date):
                    date_str = ms.date.strftime("%m/%d")
                    output.append(f"  ▼ {date_str}  {ms.name}")

        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    output.append("\n" + "=" * 80 + "\n")

    return "\n".join(output)


def print_example():
    """Print example input JSON."""
    example = {
        "project": "Website Redesign Project",
        "start_date": "2024-01-01",
        "tasks": [
            {
                "id": "T1",
                "name": "Requirements Gathering",
                "start": "2024-01-01",
                "end": "2024-01-14",
                "owner": "Sarah",
                "phase": "Planning",
                "status": "completed",
            },
            {
                "id": "T2",
                "name": "Design Wireframes",
                "start": "2024-01-15",
                "end": "2024-01-28",
                "owner": "Mike",
                "phase": "Design",
                "status": "completed",
            },
            {
                "id": "T3",
                "name": "Visual Design",
                "start": "2024-01-29",
                "end": "2024-02-18",
                "owner": "Lisa",
                "phase": "Design",
                "status": "in_progress",
            },
            {
                "id": "T4",
                "name": "Frontend Development",
                "start": "2024-02-19",
                "end": "2024-03-20",
                "owner": "Alex",
                "phase": "Development",
                "status": "not_started",
            },
            {
                "id": "T5",
                "name": "Backend Development",
                "start": "2024-02-19",
                "end": "2024-03-15",
                "owner": "Jordan",
                "phase": "Development",
                "status": "not_started",
            },
            {
                "id": "T6",
                "name": "Integration Testing",
                "start": "2024-03-21",
                "end": "2024-03-31",
                "owner": "Sam",
                "phase": "Testing",
                "status": "not_started",
            },
            {
                "id": "T7",
                "name": "User Acceptance Testing",
                "start": "2024-04-01",
                "end": "2024-04-10",
                "owner": "Sarah",
                "phase": "Testing",
                "status": "not_started",
            },
            {
                "id": "T8",
                "name": "Deployment",
                "start": "2024-04-11",
                "end": "2024-04-12",
                "owner": "Alex",
                "phase": "Launch",
                "status": "not_started",
            },
        ],
        "milestones": [
            {
                "name": "Design Approved",
                "date": "2024-02-18",
                "description": "All design mockups approved by stakeholders",
            },
            {
                "name": "Code Complete",
                "date": "2024-03-20",
                "description": "All development work finished",
            },
            {"name": "Launch", "date": "2024-04-12", "description": "Website goes live"},
        ],
    }

    print(json.dumps(example, indent=2))


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python timeline_visualizer.py <timeline_file.json> [--style STYLE]")
        print("       python timeline_visualizer.py --example")
        print("\nStyles: gantt (default), roadmap, calendar")
        print("\nFor help: python timeline_visualizer.py --help")
        sys.exit(1)

    if sys.argv[1] in ["--help", "-h", "help"]:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] in ["--example", "-e", "example"]:
        print_example()
        sys.exit(0)

    # Load timeline from file
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

    # Parse style option
    style = "gantt"
    if len(sys.argv) > 2 and sys.argv[2] in ["--style", "-s"]:
        if len(sys.argv) > 3:
            style = sys.argv[3].lower()
        else:
            print("Error: --style requires an argument")
            sys.exit(1)

    if style not in ["gantt", "roadmap", "calendar"]:
        print(f"Error: Unknown style '{style}'. Use gantt, roadmap, or calendar")
        sys.exit(1)

    # Load timeline
    try:
        project_name, tasks, milestones, start_date, end_date = load_timeline(data)
    except Exception as e:
        print(f"Error loading timeline: {e}")
        sys.exit(1)

    # Render based on style
    if style == "gantt":
        output = render_gantt_chart(project_name, tasks, milestones, start_date, end_date)
    elif style == "roadmap":
        output = render_roadmap(project_name, tasks, milestones, start_date, end_date)
    elif style == "calendar":
        output = render_calendar(project_name, tasks, milestones, start_date, end_date)

    print(output)


if __name__ == "__main__":
    main()

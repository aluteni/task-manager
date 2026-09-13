import pandas as pd
import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console=Console()

DATA_FILE="tasks_data.json"

class Task:
    
    def __init__(self, title, priority, status, due_date):
        self.title = title
        self.priority = priority
        self.status = status
        self.category = None
        self.due_date = due_date

    @property
    def title(self):
        return self._title
    
    @title.setter
    def title(self, value):
        if not str(value).strip():
            raise ValueError("Title must not be empty")
        if not any(char.isalpha() for char in value):
            raise TypeError("Title must must be a string with alphabet letters")
        self._title=value.strip().lower()

    @property
    def priority(self):
        return self._priority
    
    @priority.setter
    def priority(self, value):
        priorities = ["high", "medium", "low"]
        if not str(value).strip():
            raise ValueError("Priority must not be empty")
        if not any(char.isalpha() for char in value):
            raise TypeError("Priority must be  string with alphabet letters")
        if value.strip().lower() in priorities:
            self._priority = value.strip().lower()
        else:
            self._priority = "low"
            console.print("[yellow]Priority not recognized. Default set to 'low'.[/yellow]")
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self,value):
        statuses = ["pending", "in progress", "completed"]
        if not str(value).strip():
            raise ValueError("Status must not be empty")
        if not any(char.isalpha() for char in value):
            raise TypeError("Status must be a string with alphabet letters")
        if value.strip().lower() in statuses:
            self._status = value.strip().lower()
        else:
            self._status="pending"
            console.print("[yellow]Status not recognized. Default set to 'pending'.[/yellow]")

    
    @property
    def category(self):
        return self._category
    
    @category.setter
    def category(self, value):
        if value is not None and not isinstance(value, Category):
            raise TypeError("Category is not valid. Must be an instance of a Category class")
        self._category=value
    
    @property
    def due_date(self):
        return self._due_date
    
    @due_date.setter
    def due_date(self, value):
        try:
            self._due_date=pd.to_datetime(value, dayfirst=True)
        except Exception:
            raise ValueError("Date must be valid and in proper format")
    

    def mark_as_completed(self):
        self.status = "completed"

    def get_category_name(self):
        return self.category.name if self.category else None
    
    def update_status(self, status):
        self.status=status

    def update_priority(self, priority):
        self.priority=priority

    def reschedule(self, new_date):
        self.due_date=new_date

    def to_dict(self):
        return {
            "title": self.title,
            "priority": self.priority,
            "status": self.status,
            "category": self.category.name if self.category else None,
            "due_date": str(self.due_date)
        }

    def __str__(self):
        category = self.category.name if self.category else None
        return f"{self.title} | {self.priority} | {self.status} | {category} | {self.due_date}"

class Category:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not str(value).strip():
            raise ValueError("Name of category cannot be empty")
        if not any(char.isalpha() for char in value):
            raise TypeError("Category name must be a string with alphabet letters")
        self._name=value.strip().lower()

    def connect_to_task(self, task):
        task.category=self

    def disconnect_from_task(self, task):
        if task.category==self:
            task.category=None
        else:
            console.print("[yellow]Task does not belong to this category.[/yellow]")

    def get_tasks(self, manager):
        return manager.get_tasks_by_category(self)

    def rename(self, new_name):
        self.name=new_name

    def task_count(self, manager):
        return len(manager.get_tasks_by_category(self))

    def __str__(self):
        return self.name
            

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.categories = []

    def find_task_by_title(self, title):
        if not str(title).strip():
            raise ValueError("Task title cannot be empty")
        if not any(char.isalpha() for char in title):
            raise TypeError("Task title must be a string")
        for task in self.tasks:
            if task.title == title.strip().lower():
                return task
        return None
    
    def find_category_by_name(self, name):
        if not str(name).strip():
            raise ValueError("Category name cannot be empty")
        if not any(char.isalpha() for char in name):
            raise TypeError("Category name must be a string")
        for category in self.categories:
            if category.name == name.strip().lower():
                return category
        return None


    def task_registered(self, task):
        if not isinstance(task, Task):
            raise ValueError(f"'{task}' is not a task")
        return task in self.tasks

    def register_task(self, task):
        if self.task_registered(task):
            console.print("[yellow]Task already exists.[/yellow]")
            return
        if self.find_task_by_title(task.title):
            console.print("[yellow]A task with that title already exists.[/yellow]")
            return
        self.tasks.append(task)

    def create_category(self, category):
        if category in self.categories:
            console.print("[yellow]Category already exists.[/yellow]")
            return
        self.categories.append(category)

    def assign_task_to_category(self, task, category):
        if task in self.tasks:
            if category in self.categories:
                category.connect_to_task(task)
            else:
                console.print("[yellow]Category not found in system.[/yellow]")
        else:
            console.print("[yellow]Task not found in system.[/yellow]")
    
    def update_task_status(self, task, status):
        if self.task_registered(task):
            task.update_status(status)
        else:
            console.print("[yellow]Task not found in system.[/yellow]")

    def update_task_priority(self, task, priority):
        if self.task_registered(task):
            task.update_priority(priority)
        else:
            console.print("[yellow]Task not found in system.[/yellow]")
    def reschedule_task(self, task, date):
        if self.task_registered(task):
            task.reschedule(date)

        else:
            console.print("[yellow]Task not found in system.[/yellow]")
    def get_all_tasks(self):
        return self.tasks.copy()

    def get_all_categories(self):
        return self.categories.copy()

    def delete_task(self, task):
        if self.task_registered(task):
            self.tasks.remove(task)
        else:
            console.print("[yellow]Task not found in system.[/yellow]")

    def view_uncategorized_tasks(self):
        uncategorized_tasks = []
        for task in self.tasks:
            if task.category is None:
                uncategorized_tasks.append(task)
        return uncategorized_tasks

    def view_task(self, task):
            return str(task)
    
    def get_tasks_by_category(self, category):
        matches = []
        for task in self.tasks:
            if task.category == category:
                matches.append(task)
        return matches
    
    def save_data(self):
        data={
            "categories": [cat.name for cat in self.categories],
            "tasks": [task.to_dict() for task in self.tasks]
        }
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        
        except PermissionError:
            console.print("[red]Permission to access file is denied.[/red]\n")
        except OSError as e:
            console.print(f"[red]Failed to write to file. Error: {e}[/red]\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")

    def load_saved_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r") as f:
                data=json.load(f)

            for cat_name in data.get("categories", []):
                self.categories.append(Category(cat_name))

            for task_data in data.get("tasks", []):
                task=Task(
                        task_data["title"],
                        task_data["priority"],
                        task_data["status"],
                        task_data["due_date"]
                    )
                category_name=task_data.get("category")
                if category_name:
                    category=self.find_category_by_name(category_name)
                    if category:
                        task.category=category
                self.tasks.append(task)
            console.print(f"[green]Loaded {len(self.tasks)} task(s) and {len(self.categories)} category/categories.[/green]\n")

        except PermissionError:
            console.print("[red]Permission to access file denied.[/red]")
        except json.JSONDecodeError:
            console.print("[red]File is not a valid JSON format.[/red]")
        except KeyError:
            console.print("[red]Key given is invalid.[/red]")
        except Exception as e:
            console.print(f"[red]{e}[/red]")

def priority_color(priority):
    return {"high": "red", "medium": "yellow", "low": "green"}.get(priority, "white")

def status_color(status):
    return {"pending": "red", "in progress": "yellow", "completed": "green"}.get(status, "white")

def build_task_table(tasks, title="Tasks"):
    table = Table(title=title, header_style="bold cyan", border_style="cyan")
    table.add_column("Title", style="white", min_width=20)
    table.add_column("Priority", min_width=10)
    table.add_column("Status", min_width=15)
    table.add_column("Category", min_width=15)
    table.add_column("Due Date", min_width=20)

    for task in tasks:
        p_color = priority_color(task.priority)
        s_color = status_color(task.status)
        category = task.category.name if task.category else "—"
        table.add_row(
            task.title,
            f"[{p_color}]{task.priority}[/{p_color}]",
            f"[{s_color}]{task.status}[/{s_color}]",
            category,
            str(task.due_date)
        )
    return table

def show_task_panel(task):
    p_color = priority_color(task.priority)
    s_color = status_color(task.status)
    category = task.category.name if task.category else "None"
    content = (
        f"[bold]Title:[/bold]    {task.title}\n"
        f"[bold]Priority:[/bold] [{p_color}]{task.priority}[/{p_color}]\n"
        f"[bold]Status:[/bold]   [{s_color}]{task.status}[/{s_color}]\n"
        f"[bold]Category:[/bold] {category}\n"
        f"[bold]Due Date:[/bold] {task.due_date}"
    )
    console.print(Panel(content, title="Task Details", border_style="cyan"))

def print_menu():
    menu = (
        "[bold cyan]1.[/bold cyan]  Add task\n"
        "[bold cyan]2.[/bold cyan]  Delete task\n"
        "[bold cyan]3.[/bold cyan]  View all tasks\n"
        "[bold cyan]4.[/bold cyan]  View single task\n"
        "[bold cyan]5.[/bold cyan]  Update task status\n"
        "[bold cyan]6.[/bold cyan]  Update task priority\n"
        "[bold cyan]7.[/bold cyan]  Reschedule task\n"
        "[bold cyan]8.[/bold cyan]  Mark task as completed\n"
        "[bold cyan]9.[/bold cyan]  View uncategorized tasks\n"
        "[bold cyan]10.[/bold cyan] Create category\n"
        "[bold cyan]11.[/bold cyan] Rename category\n"
        "[bold cyan]12.[/bold cyan] Assign task to category\n"
        "[bold cyan]13.[/bold cyan] Disconnect task from category\n"
        "[bold cyan]14.[/bold cyan] View tasks by category\n"
        "[bold cyan]15.[/bold cyan] Exit"
    )
    console.print(Panel(menu, title="[bold white]TASK MANAGER[/bold white]", border_style="cyan"))

def main():
    manager=TaskManager()
    manager.load_saved_data()
    
    while True:
        print_menu()
        choice=input("Enter number of your choice: ").strip()

        if choice == "1":
            try:
                title = input("Enter task title: ")
                priority = input("Enter priority (high/medium/low): ")
                status = input("Enter status (pending/in progress/completed): ")
                due_date = input("Enter due date: ")
                task = Task(title, priority, status, due_date)
                manager.register_task(task)
                console.print(f"[green]Task '{task.title}' added successfully.[/green]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]Could not register task. Error: {e}[/red]\n")

        elif choice == "2":
            try:
                title = input("Enter title of task to delete: ")
                task = manager.find_task_by_title(title)
                if task:
                    manager.delete_task(task)
                    console.print(f"[green]Task '{title.strip().lower()}' deleted successfully.[/green]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Could not delete task. Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]Could not delete task. Error: {e}[/red]\n")

        elif choice == "3":
            tasks = manager.get_all_tasks()
            if not tasks:
                console.print("[yellow]No tasks found.[/yellow]\n")
            else:
                console.print(build_task_table(tasks, title="All Tasks"))
                console.print()
                
        elif choice == "4":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    show_task_panel(task)
                    console.print()
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")
        
        elif choice == "5":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    status = input("Enter new status (pending/in progress/completed): ")
                    manager.update_task_status(task, status)
                    console.print("[green]Status updated successfully.[/green]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")
        
        elif choice == "6":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    priority = input("Enter new priority (high/medium/low): ")
                    manager.update_task_priority(task, priority)
                    console.print("[green]Priority updated successfully.[/green]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "7":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    new_date = input("Enter new due date: ")
                    manager.reschedule_task(task, new_date)
                    console.print("[green]Task rescheduled successfully.[/green]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "8":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    task.mark_as_completed()
                    console.print(f"[green]Task '{task.title}' marked as completed.[/green]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")
        
        elif choice == "9":
            tasks = manager.view_uncategorized_tasks()
            if not tasks:
                console.print("[yellow]No uncategorized tasks found.[/yellow]\n")
            else:
                console.print(build_task_table(tasks, title="Uncategorized Tasks"))
                console.print()

        elif choice == "10":
            try:
                name = input("Enter category name: ")
                category = Category(name)
                manager.create_category(category)
                console.print(f"[green]Category '{category.name}' created successfully.[/green]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "11":
            try:
                name = input("Enter current category name: ")
                category = manager.find_category_by_name(name)
                if category:
                    new_name = input("Enter new category name: ")
                    category.rename(new_name)
                    console.print(f"[green]Category renamed to '{category.name}' successfully.[/green]\n")
                else:
                    console.print("[red]Category not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "12":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    cat_name = input("Enter category name: ")
                    category = manager.find_category_by_name(cat_name)
                    if category:
                        manager.assign_task_to_category(task, category)
                        console.print(f"[green]Task '{task.title}' assigned to '{category.name}' successfully.[/green]\n")
                    else:
                        console.print("[red]Category not found.[/red]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "13":
            try:
                title = input("Enter task title: ")
                task = manager.find_task_by_title(title)
                if task:
                    if task.category:
                        task.category.disconnect_from_task(task)
                        console.print(f"[green]Task '{task.title}' disconnected from its category.[/green]\n")
                    else:
                        console.print("[yellow]Task has no category.[/yellow]\n")
                else:
                    console.print("[red]Task not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "14":
            try:
                cat_name = input("Enter category name: ")
                category = manager.find_category_by_name(cat_name)
                if category:
                    tasks = manager.get_tasks_by_category(category)
                    if not tasks:
                        console.print(f"[yellow]No tasks found in '{category.name}'.[/yellow]\n")
                    else:
                        console.print(build_task_table(tasks, title=f"Tasks in '{category.name}'"))
                        console.print()
                else:
                    console.print("[red]Category not found.[/red]\n")
            except (ValueError, TypeError) as e:
                console.print(f"[red]Error: {e}[/red]\n")
            except Exception as e:
                console.print(f"[red]{e}[/red]")

        elif choice == "15":
            manager.save_data()
            console.print("[bold cyan]Goodbye![/bold cyan]\n")
            break
        else:
            console.print("[red]Invalid choice. Please enter a number from 1 to 15.[/red]\n")

if __name__ == "__main__":
    main()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.widgets import Button, Slider
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum
import random
import heapq

# Import the core AMR classes from previous code
class RobotStatus(Enum):
    IDLE = "idle"
    MOVING = "moving"
    WORKING = "working"
    CHARGING = "charging"
    MAINTENANCE = "maintenance"

class TaskType(Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"
    INSPECTION = "inspection"
    CLEANING = "cleaning"

@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Task:
    id: str
    task_type: TaskType
    start_pos: Position
    end_pos: Position
    priority: int
    estimated_duration: float
    assigned_robot: Optional[str] = None
    created_time: datetime = None
    
    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()

class Robot:
    def __init__(self, robot_id: str, initial_pos: Position, max_battery: float = 100.0):
        self.id = robot_id
        self.position = initial_pos
        self.status = RobotStatus.IDLE
        self.battery_level = max_battery
        self.max_battery = max_battery
        self.speed = 2.0
        self.current_task: Optional[Task] = None
        self.path: List[Position] = []
        self.total_distance_traveled = 0.0
        self.tasks_completed = 0
        self.last_maintenance = datetime.now()
        self.target_position: Optional[Position] = None
        
    def move_towards_target(self, target: Position, dt: float) -> bool:
        if self.battery_level <= 5:
            self.status = RobotStatus.CHARGING
            return False
            
        distance = self.position.distance_to(target)
        if distance < 0.5:
            self.position = Position(target.x, target.y)
            return True
            
        move_distance = min(self.speed * dt, distance)
        direction_x = (target.x - self.position.x) / distance
        direction_y = (target.y - self.position.y) / distance
        
        self.position.x += direction_x * move_distance
        self.position.y += direction_y * move_distance
        
        self.total_distance_traveled += move_distance
        self.battery_level = max(0, self.battery_level - move_distance * 0.1)
        
        return False
        
    def assign_task(self, task: Task):
        self.current_task = task
        self.status = RobotStatus.MOVING
        self.target_position = task.start_pos
        task.assigned_robot = self.id
        
    def complete_current_task(self):
        if self.current_task:
            self.tasks_completed += 1
            self.current_task = None
            self.status = RobotStatus.IDLE
            self.target_position = None

class PathPlanner:
    def __init__(self, grid_width: int, grid_height: int, obstacles: List[Tuple[int, int]] = None):
        self.width = grid_width
        self.height = grid_height
        self.obstacles = set(obstacles) if obstacles else set()

class TaskScheduler:
    def __init__(self):
        self.pending_tasks: List[Task] = []
        
    def add_task(self, task: Task):
        self.pending_tasks.append(task)
        self.pending_tasks.sort(key=lambda t: t.priority, reverse=True)
        
    def assign_optimal_robot(self, robots: List[Robot]) -> Optional[Tuple[Robot, Task]]:
        if not self.pending_tasks:
            return None
            
        available_robots = [r for r in robots if r.status == RobotStatus.IDLE and r.battery_level > 20]
        if not available_robots:
            return None
            
        best_assignment = None
        best_score = float('inf')
        
        for task in self.pending_tasks:
            for robot in available_robots:
                distance = robot.position.distance_to(task.start_pos)
                battery_penalty = (100 - robot.battery_level) * 0.1
                score = distance + battery_penalty
                
                if score < best_score:
                    best_score = score
                    best_assignment = (robot, task)
        
        if best_assignment:
            robot, task = best_assignment
            self.pending_tasks.remove(task)
            return best_assignment
        
        return None

class AMRFleetManager:
    def __init__(self, grid_width: int = 50, grid_height: int = 30):
        self.robots: List[Robot] = []
        self.task_scheduler = TaskScheduler()
        self.path_planner = PathPlanner(grid_width, grid_height)
        self.charging_stations = [Position(5, 5), Position(45, 5), Position(25, 25)]
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.total_tasks_completed = 0
        self.fleet_efficiency = 0.0
        self.simulation_running = False
        
    def add_robot(self, robot: Robot):
        self.robots.append(robot)
        
    def generate_random_task(self) -> Task:
        task_types = list(TaskType)
        start_pos = Position(
            random.uniform(2, self.grid_width-2),
            random.uniform(2, self.grid_height-2)
        )
        end_pos = Position(
            random.uniform(2, self.grid_width-2),
            random.uniform(2, self.grid_height-2)
        )
        
        return Task(
            id=f"T{random.randint(1000, 9999)}",
            task_type=random.choice(task_types),
            start_pos=start_pos,
            end_pos=end_pos,
            priority=random.randint(1, 5),
            estimated_duration=random.uniform(5, 30)
        )
    
    def update_fleet(self, dt: float):
        # Handle task assignments
        assignment = self.task_scheduler.assign_optimal_robot(self.robots)
        if assignment:
            robot, task = assignment
            robot.assign_task(task)
        
        # Update each robot
        for robot in self.robots:
            if robot.status == RobotStatus.MOVING and robot.target_position:
                if robot.move_towards_target(robot.target_position, dt):
                    if robot.current_task:
                        if robot.target_position == robot.current_task.start_pos:
                            # Reached pickup point, now go to delivery
                            robot.target_position = robot.current_task.end_pos
                            robot.status = RobotStatus.WORKING
                        else:
                            # Completed delivery
                            robot.complete_current_task()
                    else:
                        robot.status = RobotStatus.IDLE
                        
            elif robot.status == RobotStatus.WORKING and robot.target_position:
                if robot.move_towards_target(robot.target_position, dt):
                    robot.complete_current_task()
                    
            elif robot.status == RobotStatus.CHARGING:
                # Find nearest charging station and move there
                if not robot.target_position:
                    nearest_station = min(self.charging_stations, 
                                        key=lambda s: robot.position.distance_to(s))
                    robot.target_position = nearest_station
                
                if robot.move_towards_target(robot.target_position, dt):
                    # At charging station, charge battery
                    robot.battery_level = min(robot.max_battery, robot.battery_level + 20 * dt)
                    if robot.battery_level >= robot.max_battery * 0.9:
                        robot.status = RobotStatus.IDLE
                        robot.target_position = None
        
        # Update metrics
        self.total_tasks_completed = sum(r.tasks_completed for r in self.robots)
        active_robots = len([r for r in self.robots if r.status != RobotStatus.IDLE])
        self.fleet_efficiency = (active_robots / len(self.robots)) * 100 if self.robots else 0
    
    def get_fleet_status(self) -> Dict:
        status_counts = {}
        for status in RobotStatus:
            status_counts[status.value] = len([r for r in self.robots if r.status == status])
        
        return {
            'total_robots': len(self.robots),
            'status_distribution': status_counts,
            'pending_tasks': len(self.task_scheduler.pending_tasks),
            'total_tasks_completed': self.total_tasks_completed,
            'fleet_efficiency': round(self.fleet_efficiency, 2),
            'average_battery': round(np.mean([r.battery_level for r in self.robots]), 2) if self.robots else 0
        }

class AMRDashboard:
    def __init__(self):
        self.fleet_manager = AMRFleetManager()
        self.setup_fleet()
        
        # Setup matplotlib figure
        self.fig, ((self.ax_main, self.ax_battery), (self.ax_status, self.ax_metrics)) = plt.subplots(2, 2, figsize=(16, 10))
        self.fig.suptitle('AMR Fleet Management Dashboard', fontsize=16, fontweight='bold')
        
        # Data for plots
        self.time_data = []
        self.efficiency_data = []
        self.battery_data = []
        self.task_data = []
        
        # Colors for different robot statuses
        self.status_colors = {
            RobotStatus.IDLE: 'green',
            RobotStatus.MOVING: 'blue',
            RobotStatus.WORKING: 'orange',
            RobotStatus.CHARGING: 'red',
            RobotStatus.MAINTENANCE: 'purple'
        }
        
        # Setup plots
        self.setup_plots()
        
        # Animation
        self.ani = animation.FuncAnimation(self.fig, self.update_dashboard, 
                                         interval=100, blit=False, cache_frame_data=False)
        
        # Control panel
        self.setup_controls()
        
    def setup_fleet(self):
        """Initialize the robot fleet"""
        robot_positions = [
            Position(10, 10), Position(20, 15), Position(30, 8),
            Position(40, 20), Position(15, 25), Position(35, 12)
        ]
        
        for i, pos in enumerate(robot_positions):
            robot = Robot(f"AMR-{i+1:02d}", pos)
            self.fleet_manager.add_robot(robot)
        
        # Add initial tasks
        for _ in range(8):
            task = self.fleet_manager.generate_random_task()
            self.fleet_manager.task_scheduler.add_task(task)
    
    def setup_plots(self):
        """Setup all dashboard plots"""
        # Main fleet view
        self.ax_main.set_xlim(0, self.fleet_manager.grid_width)
        self.ax_main.set_ylim(0, self.fleet_manager.grid_height)
        self.ax_main.set_title('Fleet Overview', fontweight='bold')
        self.ax_main.set_xlabel('X Position')
        self.ax_main.set_ylabel('Y Position')
        self.ax_main.grid(True, alpha=0.3)
        
        # Draw charging stations
        for station in self.fleet_manager.charging_stations:
            charging_circle = Circle((station.x, station.y), 2, color='yellow', alpha=0.6)
            self.ax_main.add_patch(charging_circle)
            self.ax_main.text(station.x, station.y-3, 'CHARGE', ha='center', fontsize=8)
        
        # Battery levels
        self.ax_battery.set_title('Robot Battery Levels', fontweight='bold')
        self.ax_battery.set_xlabel('Robot ID')
        self.ax_battery.set_ylabel('Battery %')
        self.ax_battery.set_ylim(0, 100)
        
        # Status distribution
        self.ax_status.set_title('Fleet Status Distribution', fontweight='bold')
        
        # Performance metrics
        self.ax_metrics.set_title('Fleet Performance Over Time', fontweight='bold')
        self.ax_metrics.set_xlabel('Time (seconds)')
        self.ax_metrics.set_ylabel('Efficiency %')
        self.ax_metrics.set_ylim(0, 100)
    
    def setup_controls(self):
        """Setup control buttons"""
        # Add task button
        ax_add_task = plt.axes([0.02, 0.95, 0.1, 0.04])
        self.btn_add_task = Button(ax_add_task, 'Add Task')
        self.btn_add_task.on_clicked(self.add_random_task)
        
        # Emergency stop button
        ax_emergency = plt.axes([0.13, 0.95, 0.1, 0.04])
        self.btn_emergency = Button(ax_emergency, 'Emergency Stop')
        self.btn_emergency.on_clicked(self.emergency_stop)
        
        # Speed control slider
        ax_speed = plt.axes([0.25, 0.95, 0.15, 0.03])
        self.speed_slider = Slider(ax_speed, 'Speed', 0.1, 3.0, valinit=1.0)
        self.speed_slider.on_changed(self.update_speed)
    
    def add_random_task(self, event):
        """Add a random task to the queue"""
        task = self.fleet_manager.generate_random_task()
        self.fleet_manager.task_scheduler.add_task(task)
    
    def emergency_stop(self, event):
        """Emergency stop all robots"""
        for robot in self.fleet_manager.robots:
            robot.status = RobotStatus.IDLE
            robot.target_position = None
            robot.current_task = None
    
    def update_speed(self, val):
        """Update robot speeds"""
        for robot in self.fleet_manager.robots:
            robot.speed = val * 2.0
    
    def update_dashboard(self, frame):
        """Update all dashboard components"""
        # Update fleet simulation
        self.fleet_manager.update_fleet(0.1)
        
        # Clear plots
        self.ax_main.clear()
        self.ax_battery.clear()
        self.ax_status.clear()
        
        # Redraw static elements
        self.setup_plots()
        
        # Draw robots
        for robot in self.fleet_manager.robots:
            color = self.status_colors[robot.status]
            
            # Robot position
            robot_circle = Circle((robot.position.x, robot.position.y), 1, 
                                color=color, alpha=0.8)
            self.ax_main.add_patch(robot_circle)
            
            # Robot ID label
            self.ax_main.text(robot.position.x, robot.position.y + 1.5, robot.id, 
                            ha='center', fontsize=8, fontweight='bold')
            
            # Target line
            if robot.target_position:
                self.ax_main.plot([robot.position.x, robot.target_position.x],
                                [robot.position.y, robot.target_position.y],
                                '--', color=color, alpha=0.5)
        
        # Draw pending tasks
        for task in self.fleet_manager.task_scheduler.pending_tasks:
            task_rect = Rectangle((task.start_pos.x-0.5, task.start_pos.y-0.5), 1, 1,
                                color='red', alpha=0.6)
            self.ax_main.add_patch(task_rect)
            self.ax_main.text(task.start_pos.x, task.start_pos.y-1.5, f'P{task.priority}',
                            ha='center', fontsize=6)
        
        # Battery levels bar chart
        robot_ids = [robot.id for robot in self.fleet_manager.robots]
        battery_levels = [robot.battery_level for robot in self.fleet_manager.robots]
        colors = [self.status_colors[robot.status] for robot in self.fleet_manager.robots]
        
        bars = self.ax_battery.bar(robot_ids, battery_levels, color=colors, alpha=0.7)
        self.ax_battery.axhline(y=20, color='red', linestyle='--', alpha=0.8, label='Low Battery')
        self.ax_battery.legend()
        
        # Add battery percentage labels on bars
        for bar, level in zip(bars, battery_levels):
            height = bar.get_height()
            self.ax_battery.text(bar.get_x() + bar.get_width()/2., height + 1,
                               f'{level:.0f}%', ha='center', va='bottom', fontsize=8)
        
        # Status distribution pie chart
        status_counts = self.fleet_manager.get_fleet_status()['status_distribution']
        labels = []
        sizes = []
        colors_pie = []
        
        for status, count in status_counts.items():
            if count > 0:
                labels.append(f"{status.title()} ({count})")
                sizes.append(count)
                colors_pie.append(self.status_colors[RobotStatus(status)])
        
        if sizes:
            self.ax_status.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                             startangle=90)
        
        # Performance metrics over time
        current_time = len(self.time_data) * 0.1
        self.time_data.append(current_time)
        self.efficiency_data.append(self.fleet_manager.fleet_efficiency)
        
        # Keep only last 100 data points
        if len(self.time_data) > 100:
            self.time_data.pop(0)
            self.efficiency_data.pop(0)
        
        self.ax_metrics.clear()
        self.ax_metrics.set_title('Fleet Performance Over Time', fontweight='bold')
        self.ax_metrics.set_xlabel('Time (seconds)')
        self.ax_metrics.set_ylabel('Efficiency %')
        self.ax_metrics.set_ylim(0, 100)
        self.ax_metrics.plot(self.time_data, self.efficiency_data, 'b-', linewidth=2)
        self.ax_metrics.grid(True, alpha=0.3)
        
        # Add performance text
        status = self.fleet_manager.get_fleet_status()
        metrics_text = f"""Tasks Completed: {status['total_tasks_completed']}
Pending Tasks: {status['pending_tasks']}
Fleet Efficiency: {status['fleet_efficiency']}%
Avg Battery: {status['average_battery']}%"""
        
        self.ax_metrics.text(0.02, 0.98, metrics_text, transform=self.ax_metrics.transAxes,
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Automatically add new tasks occasionally
        if frame % 100 == 0:  # Every 10 seconds
            self.add_random_task(None)
        
        try:
            plt.tight_layout()
        except:
            pass  # Ignore layout warnings from interactive elements
    
    def run(self):
        """Start the dashboard"""
        plt.show()

# Enhanced Control Panel using tkinter
class AMRControlPanel:
    def __init__(self, fleet_manager: AMRFleetManager):
        self.fleet_manager = fleet_manager
        self.root = tk.Tk()
        self.root.title("AMR Fleet Control Panel")
        self.root.geometry("400x600")
        
        self.setup_gui()
        
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Fleet status frame
        status_frame = ttk.LabelFrame(main_frame, text="Fleet Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = tk.Text(status_frame, height=8, width=45)
        self.status_text.grid(row=0, column=0)
        
        # Control buttons frame
        control_frame = ttk.LabelFrame(main_frame, text="Fleet Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="Add Random Task", 
                  command=self.add_task).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Emergency Stop", 
                  command=self.emergency_stop).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Resume Operations", 
                  command=self.resume_operations).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Send All to Charge", 
                  command=self.charge_all).grid(row=1, column=1, padx=5, pady=5)
        
        # Robot details frame
        robot_frame = ttk.LabelFrame(main_frame, text="Robot Details", padding="10")
        robot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Robot selection
        self.robot_var = tk.StringVar()
        self.robot_combo = ttk.Combobox(robot_frame, textvariable=self.robot_var, width=20)
        self.robot_combo.grid(row=0, column=0, padx=5)
        
        ttk.Button(robot_frame, text="Get Robot Info", 
                  command=self.show_robot_info).grid(row=0, column=1, padx=5)
        
        self.robot_info_text = tk.Text(robot_frame, height=6, width=45)
        self.robot_info_text.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Update timer
        self.update_display()
        
    def add_task(self):
        task = self.fleet_manager.generate_random_task()
        self.fleet_manager.task_scheduler.add_task(task)
        messagebox.showinfo("Task Added", f"Added task {task.id} ({task.task_type.value})")
    
    def emergency_stop(self):
        for robot in self.fleet_manager.robots:
            robot.status = RobotStatus.IDLE
            robot.target_position = None
            robot.current_task = None
        messagebox.showwarning("Emergency Stop", "All robots stopped!")
    
    def resume_operations(self):
        messagebox.showinfo("Resume", "Operations resumed")
    
    def charge_all(self):
        for robot in self.fleet_manager.robots:
            if robot.battery_level < 90:
                robot.status = RobotStatus.CHARGING
                robot.target_position = None
        messagebox.showinfo("Charging", "All robots sent to charging stations")
    
    def show_robot_info(self):
        robot_id = self.robot_var.get()
        robot = next((r for r in self.fleet_manager.robots if r.id == robot_id), None)
        
        if robot:
            info = f"""Robot ID: {robot.id}
Status: {robot.status.value}
Position: ({robot.position.x:.1f}, {robot.position.y:.1f})
Battery: {robot.battery_level:.1f}%
Tasks Completed: {robot.tasks_completed}
Distance Traveled: {robot.total_distance_traveled:.1f}
Current Task: {robot.current_task.id if robot.current_task else 'None'}"""
            
            self.robot_info_text.delete(1.0, tk.END)
            self.robot_info_text.insert(1.0, info)
    
    def update_display(self):
        # Update fleet status
        status = self.fleet_manager.get_fleet_status()
        status_info = f"""Total Robots: {status['total_robots']}
Active Tasks: {status['total_tasks_completed']}
Pending Tasks: {status['pending_tasks']}
Fleet Efficiency: {status['fleet_efficiency']}%
Average Battery: {status['average_battery']}%

Status Distribution:"""
        
        for status_type, count in status['status_distribution'].items():
            status_info += f"\n  {status_type.title()}: {count}"
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_info)
        
        # Update robot combo box
        robot_ids = [robot.id for robot in self.fleet_manager.robots]
        self.robot_combo['values'] = robot_ids
        if robot_ids and not self.robot_var.get():
            self.robot_var.set(robot_ids[0])
        
        # Schedule next update
        self.root.after(1000, self.update_display)
    
    def run(self):
        self.root.mainloop()

def main():
    """Main function to run the AMR Dashboard"""
    print("Starting AMR Fleet Management Dashboard...")
    
    # Create and run dashboard
    dashboard = AMRDashboard()
    
    # Optionally create control panel in separate thread
    def run_control_panel():
        control_panel = AMRControlPanel(dashboard.fleet_manager)
        control_panel.run()
    
    # Uncomment to run control panel alongside dashboard
    # control_thread = threading.Thread(target=run_control_panel, daemon=True)
    # control_thread.start()
    
    # Run main dashboard
    dashboard.run()

if __name__ == "__main__":
    main()
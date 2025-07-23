# 🤖 AMR Fleet Management & Path Optimization Dashboard

A comprehensive Python-based dashboard for managing Autonomous Mobile Robot (AMR) fleets with real-time visualization, intelligent task scheduling, and performance monitoring.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dashboard Components](#dashboard-components)
- [System Architecture](#system-architecture)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project simulates and manages a fleet of Autonomous Mobile Robots (AMRs) operating in dynamic environments such as warehouses or factory floors. The system provides real-time monitoring, intelligent path planning, automatic task assignment, and comprehensive performance analytics.

### Key Capabilities
- **Fleet Monitoring**: Real-time tracking of multiple robotic units
- **AI-Driven Optimization**: Intelligent path planning and task assignment
- **Battery Management**: Proactive charging and maintenance scheduling
- **Performance Analytics**: Comprehensive metrics and efficiency tracking
- **Interactive Control**: Manual override and emergency controls

## ✨ Features

### 🎛️ **Real-Time Dashboard**
- Live robot position tracking
- Battery level monitoring with visual indicators
- Fleet status distribution (idle, moving, working, charging)
- Performance metrics over time
- Interactive control panel

### 🧠 **Intelligent Systems**
- **A* Pathfinding Algorithm**: Optimal route planning with obstacle avoidance
- **Smart Task Scheduling**: Priority-based assignment considering robot proximity and battery
- **Autonomous Charging**: Automatic battery management and charging station routing
- **Dynamic Load Balancing**: Efficient distribution of workload across fleet

### 📊 **Monitoring & Analytics**
- Fleet efficiency tracking
- Task completion rates
- Distance traveled metrics
- Battery consumption analysis
- Robot utilization statistics

### 🎮 **Interactive Controls**
- Manual task creation and assignment
- Emergency stop functionality
- Speed adjustment controls
- Individual robot monitoring
- Fleet-wide commands

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Dependencies
```bash
pip install numpy matplotlib tkinter
```

### Clone Repository
```bash
git clone <repository-url>
cd amr-fleet-management
```

### Verify Installation
```bash
python amr_dashboard.py
```

## ⚡ Quick Start

### 1. Basic Usage
```bash
# Run the main dashboard
python amr_dashboard.py
```

### 2. Dashboard Controls
- **Add Task**: Click to create new random tasks
- **Emergency Stop**: Immediately halt all robot operations
- **Speed Slider**: Adjust robot movement speed (0.1x - 3.0x)

### 3. Fleet Initialization
The system automatically creates:
- 6 AMR robots with unique IDs (AMR-01 to AMR-06)
- 3 charging stations at strategic locations
- 8 initial tasks for immediate assignment

## 📊 Dashboard Components

### Fleet Overview Map
- **Robots**: Colored circles representing current status
  - 🟢 Green: Idle
  - 🔵 Blue: Moving
  - 🟠 Orange: Working
  - 🔴 Red: Charging
  - 🟣 Purple: Maintenance
- **Charging Stations**: Yellow circles with "CHARGE" labels
- **Tasks**: Red squares with priority indicators
- **Paths**: Dotted lines showing robot destinations

### Battery Monitor
- Individual robot battery levels
- Color-coded status indicators
- Low battery warning threshold (20%)
- Real-time percentage display

### Status Distribution
- Pie chart showing fleet activity breakdown
- Live percentage calculations
- Color-coded status categories

### Performance Metrics
- Real-time efficiency tracking
- Task completion counters
- Fleet utilization rates
- Historical performance graphs

## 🏗️ System Architecture

### Core Components

#### 1. Robot Class
```python
class Robot:
    - position: Current coordinates
    - battery_level: Power status (0-100%)
    - status: Current operation state
    - current_task: Assigned work
    - performance_metrics: Distance, tasks completed
```

#### 2. Task Management
```python
class Task:
    - task_type: PICKUP, DELIVERY, INSPECTION, CLEANING
    - priority: 1-5 priority levels
    - positions: Start and end coordinates
    - assignment: Robot allocation
```

#### 3. Fleet Manager
```python
class AMRFleetManager:
    - Robot fleet coordination
    - Task scheduling and assignment
    - Performance monitoring
    - Charging station management
```

#### 4. Path Planning
```python
class PathPlanner:
    - A* pathfinding algorithm
    - Obstacle avoidance
    - Route optimization
```

### Data Flow
```
Task Creation → Task Scheduler → Robot Assignment → Path Planning → Execution → Monitoring
```

## 💡 Usage Examples

### Adding Custom Tasks
```python
# Create a custom task
task = Task(
    id="CUSTOM_001",
    task_type=TaskType.DELIVERY,
    start_pos=Position(10, 15),
    end_pos=Position(35, 20),
    priority=3,
    estimated_duration=25.0
)

# Add to queue
fleet_manager.task_scheduler.add_task(task)
```

### Robot Control
```python
# Get robot by ID
robot = fleet_manager.get_robot("AMR-01")

# Manual task assignment
robot.assign_task(custom_task)

# Emergency stop
robot.status = RobotStatus.IDLE
robot.target_position = None
```

### Fleet Monitoring
```python
# Get fleet status
status = fleet_manager.get_fleet_status()
print(f"Fleet Efficiency: {status['fleet_efficiency']}%")
print(f"Tasks Completed: {status['total_tasks_completed']}")
```

## ⚙️ Configuration

### Fleet Parameters
```python
# Fleet size and workspace
GRID_WIDTH = 50          # Workspace width
GRID_HEIGHT = 30         # Workspace height
NUM_ROBOTS = 6           # Fleet size
CHARGING_STATIONS = 3    # Number of charging points

# Robot specifications
MAX_BATTERY = 100.0      # Battery capacity
ROBOT_SPEED = 2.0        # Movement speed
LOW_BATTERY_THRESHOLD = 20.0  # Charging trigger
```

### Task Configuration
```python
# Task generation settings
TASK_PRIORITIES = [1, 2, 3, 4, 5]  # Priority levels
TASK_DURATION_RANGE = (10, 60)     # Duration in seconds
AUTO_TASK_INTERVAL = 100           # Auto-generation frequency
```

### Performance Tuning
```python
# Update frequencies
DASHBOARD_UPDATE_RATE = 100        # milliseconds
SIMULATION_TIMESTEP = 0.1          # seconds
PERFORMANCE_HISTORY_LENGTH = 100   # data points
```

## 📚 API Reference
### AMRFleetManager Methods

#### Fleet Operations
- `add_robot(robot)`: Add robot to fleet
- `update_fleet(dt)`: Update simulation step
- `get_fleet_status()`: Get current status summary
- `generate_random_task()`: Create random task

#### Task Management
- `assign_optimal_robot(robots)`: Find best robot for task
- `add_task(task)`: Add task to queue
- `get_pending_tasks()`: Get unassigned tasks

#### Monitoring
- `get_robot_metrics(robot_id)`: Individual robot statistics
- `calculate_fleet_efficiency()`: Overall performance metrics
- `get_battery_status()`: Fleet battery summary

### Robot Methods

#### Control
- `assign_task(task)`: Assign work to robot
- `move_towards_target(target, dt)`: Execute movement
- `complete_current_task()`: Finish assigned work

#### Status
- `get_position()`: Current coordinates
- `get_battery_level()`: Power remaining
- `get_status()`: Current operation state

## 🔧 Troubleshooting
### Common Issues

#### Dashboard Not Displaying
```bash
# Check matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Install GUI backend if needed
pip install tkinter
```

#### Layout Warnings
```python
# Ignore harmless tight_layout warnings
import warnings
warnings.filterwarnings("ignore", message="This figure includes Axes")
```

#### Performance Issues
- Reduce update frequency for large fleets
- Limit performance history length
- Close unused plots and windows

### System Requirements
- **RAM**: Minimum 2GB (4GB recommended)
- **CPU**: Multi-core processor recommended
- **Display**: Minimum 1024x768 resolution
- **Python**: Version 3.7 or higher

## 🤝 Contributing
- We welcome contributions! Please follow these steps:
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** and add tests
4. **Commit changes**: `git commit -m "Add new feature"`
5. **Push to branch**: `git push origin feature/new-feature`
6. **Submit pull request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

### Areas for Contribution
- Advanced pathfinding algorithms
- Machine learning integration
- Database connectivity
- Web-based dashboard
- Multi-floor navigation
- Collision avoidance improvements

## 📈 Future Enhancements

### Planned Features
- [ ] **3D Visualization**: Multi-floor facility support
- [ ] **Machine Learning**: Predictive task scheduling
- [ ] **Web Interface**: Browser-based control panel
- [ ] **Database Integration**: Historical data storage
- [ ] **REST API**: External system integration
- [ ] **Mobile App**: Remote monitoring capabilities

### Advanced Algorithms
- [ ] **Multi-Agent Path Finding (MAPF)**
- [ ] **Reinforcement Learning** for task optimization
- [ ] **Swarm Intelligence** coordination
- [ ] **Predictive Maintenance** scheduling

## 📄 License
- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- **A* Algorithm**: Based on Hart, Nilsson, and Raphael's pathfinding research
- **Matplotlib**: For excellent visualization capabilities
- **NumPy**: For efficient numerical computations
- **Python Community**: For comprehensive libraries and support


- **Built with ❤️ for autonomous robotics and intelligent fleet management**
---




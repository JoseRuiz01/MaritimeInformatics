# mission_manager.py (conceptual outline)
from dronekit import connect, VehicleMode, Command
import time
from mqtt_handler import MQTTHandler  # Reuse from previous projects
from pymavlink import mavutil

class MissionManager:
    def __init__(self, vehicle, mqtt_handler):
        self.vehicle = vehicle
        self.mqtt_handler = mqtt_handler
        self.mission_waypoints = []
    
    
    
    def load_mission_from_file(self, filename):
        """
        Parse mission file and create waypoint list
        
        Steps to implement:
        1. Open and read the file
        2. Parse each line (skip comments starting with #)
        3. Extract lat, lon, alt values
        4. Store in mission_waypoints list
        """
        waypoints = []
        
        try:
            with open(filename, 'r') as file:
                # - Read file line by line
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split(',')
                    if len(parts) != 3:
                        continue
                    # - Parse coordinates
                    lat, lon, alt = map(float, parts)
                    waypoints.append((lat, lon, alt))
            self.mission_waypoints = waypoints

            # - Publish mission_loaded message
            self.mqtt_handler.publish({
                "type": "mission_loaded",
                "waypoint_count": len(waypoints),
                "estimated_distance": self.estimate_mission_distance()
            })

        # - Handle errors gracefully
        except Exception as e:
            print(f"Error loading mission: {e}")
        return waypoints
    
    
    
    def upload_mission_to_vehicle(self):
        """
        Upload waypoints to vehicle using DroneKit commands
        
        Research needed:
        - How to clear existing mission
        - How to create mission items/commands
        - How to upload to vehicle
        - How to verify upload success
        
        Key DroneKit concepts to explore:
        - vehicle.commands
        - Command objects
        - MAV_CMD_NAV_WAYPOINT
        """
        print("Uploading mission to vehicle...")
        
        # - Clear current mission
        self.vehicle.commands.clear()
        self.vehicle.commands.wait_ready()  
        
        # - Create command sequence
        for wp in self.mission_waypoints:
            lat, lon, alt = wp
            cmd = Command(
                0, 0, 0,                              # target system, component, sequence
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0, 0,                                 # current, autocontinue
                0, 0, 0, 0,                           # params 1-4 (unused here)
                lat, lon, alt                         # params 5-7 (coordinates)
            )
            self.vehicle.commands.add(cmd)
            
        # - Upload to vehicle
        self.vehicle.commands.upload()
        print("Mission uploaded successfully.")

        # - Publish MQTT update
        self.mqtt_handler.publish({
            "type": "mission_uploaded",
            "waypoint_count": len(self.mission_waypoints),
            "status": "success"
        })
        
    
    
    def start_mission(self):
        """
        Arm vehicle and set AUTO mode
        """
        # Arm vehicle if not armed
        if not self.vehicle.armed:
            print("Arming vehicle...")
            self.vehicle.armed = True
            # Wait for arming
            while not self.vehicle.armed:
                time.sleep(1)
            
        # Set AUTO mode
        print("Setting AUTO mode...")
        self.vehicle.mode = VehicleMode("AUTO")
        # Wait for mode change
        while self.vehicle.mode.name != "AUTO":
            time.sleep(1)

        self.mission_start_time = time.time()
    
    
    
    def monitor_mission_progress(self):
        """
        Track mission execution and publish updates
        
        Key parameters to monitor:
        - Current waypoint index
        - Total waypoints
        - Distance to next waypoint
        - Mission completion status
        
        MQTT updates could include:
        - Progress percentage
        - Current waypoint
        - ETA to completion
        """
            
        total_wp = len(self.mission_waypoints)

        while self.vehicle.mode.name == "AUTO":
            # - Get current mission status
            next_wp = self.vehicle.commands.next  
            # - Calculate progress
            progress_percent = (next_wp / total_wp) * 100 if total_wp > 0 else 0

            # - Publish via MQTT
            self.mqtt_handler.publish({
                "type": "mission_progress",
                "current_waypoint": next_wp,
                "total_waypoints": total_wp,
                "progress_percent": round(progress_percent, 2),
                "mode": self.vehicle.mode.name
            })

            # - Detect mission complete
            if next_wp >= total_wp:
                self.mqtt_handler.publish({
                    "type": "mission_complete",
                    "total_time": round(time.time() - self.mission_start_time),
                    "final_position": {
                        "lat": self.vehicle.location.global_relative_frame.lat,
                        "lon": self.vehicle.location.global_relative_frame.lon
                    }
                })
                break

            time.sleep(5)


import os
import sys
import threading
import time

import traci
import sumolib
import math

WEST = "west"
EAST = "east"
NORTH = "north"
SOUTH = "south"

instruction_forward = "ileri"
instruction_right = "sağ"
instruction_left = "sol"
instruction_backward = "geri"


class Sumo():
    def __init__(self, ui):
        self.ui = ui
        self.netPath = "sumoVol2/aaa.net.xml"
        self.sumocfgPath = r"sumoVol2/aaa.sumocfg"
        self.sumoBinary = r'C:\Eclipse\Sumo\bin\sumo-gui.exe'
        self.sumoCmd = [self.sumoBinary, "-c", self.sumocfgPath, "--start", "-Q"]
        self.net = sumolib.net.readNet(self.netPath)

        sys.path.append(os.path.join('C:\Program Files (x86)\Eclipse\Sumo', 'tools'))

        self.vehicle_id = None
        self.vehicle_edge_id = None
        self.vehicle_to_node_id = None
        self.vehicle_from_node_id = None
        self.vehicle_direction = None
        self.vehicle_stop = True

        self.lock = threading.Lock()
        self.instruction = ""
        self.runInstruction = False

        self.stop = False

    def calculate_angle(self, from_node, to_node):
        from_pos = from_node.getCoord()
        to_pos = to_node.getCoord()

        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]

        angle = math.degrees(math.atan2(dy, dx)) % 360

        return angle

    def get_vehicle_direction(self):
        angle = self.calculate_angle(self.net.getNode(self.vehicle_from_node_id),
                                     self.net.getNode(self.vehicle_to_node_id))

        if angle >= -45 and angle < 45:
            current_direction = EAST
        elif angle >= 45 and angle < 135:
            current_direction = NORTH
        elif angle >= 135 and angle < 225:
            current_direction = WEST
        else:
            current_direction = SOUTH

        return current_direction

    def get_adjacent_edges(self, junction):
        west_list = []
        east_list = []
        north_list = []
        south_list = []

        # TODO: liste sıralaması yapılmalı
        angle_threshold = 45
        for edge in junction.getOutgoing():
            connected_junction = edge.getToNode()
            angle = self.calculate_angle(junction, connected_junction)

            if 180 - angle_threshold <= angle <= 180 + angle_threshold:  # west
                west_list.append(edge.getID())
            if -angle_threshold <= angle <= angle_threshold:  # east
                east_list.append(edge.getID())
            if 90 - angle_threshold <= angle <= 90 + angle_threshold:  # north
                north_list.append(edge.getID())
            if 270 - angle_threshold <= angle <= 270 + angle_threshold:  # south
                south_list.append(edge.getID())

        adjacent_edges = {WEST: west_list, EAST: east_list, NORTH: north_list, SOUTH: south_list}
        return adjacent_edges

    def get_relative_direction(self, instruction):
        if instruction == instruction_forward:
            return self.vehicle_direction
        elif instruction == instruction_right:
            if self.vehicle_direction == WEST:
                return NORTH
            elif self.vehicle_direction == EAST:
                return SOUTH
            elif self.vehicle_direction == NORTH:
                return EAST
            elif self.vehicle_direction == SOUTH:
                return WEST
        elif instruction == instruction_left:
            if self.vehicle_direction == WEST:
                return SOUTH
            elif self.vehicle_direction == EAST:
                return NORTH
            elif self.vehicle_direction == NORTH:
                return WEST
            elif self.vehicle_direction == SOUTH:
                return EAST
        elif instruction == instruction_backward:
            if self.vehicle_direction == WEST:
                return EAST
            elif self.vehicle_direction == EAST:
                return WEST
            elif self.vehicle_direction == NORTH:
                return SOUTH
            elif self.vehicle_direction == SOUTH:
                return NORTH
        else:
            return ""

    def set_route_by_instruction(self, instruction):
        if(instruction):
            if len(traci.vehicle.getIDList()) > 0:
                self.vehicle_edge_id = traci.vehicle.getRoadID(self.vehicle_id)
                self.vehicle_to_node_id = self.net.getEdge(self.vehicle_edge_id).getToNode().getID()
                self.vehicle_from_node_id = self.net.getEdge(self.vehicle_edge_id).getFromNode().getID()
                self.vehicle_direction = self.get_vehicle_direction()

                nextJunction = self.net.getNode(self.vehicle_to_node_id)
                adjacent_junctions = self.get_adjacent_edges(nextJunction)

                direction = self.get_relative_direction(instruction)
                if direction in adjacent_junctions and len(adjacent_junctions[direction]) > 0:
                    traci.vehicle.changeTarget(self.vehicle_id, adjacent_junctions[direction][0])
                    self.vehicle_stop = False
                else:
                    self.ui.insertRow("yol yok!","no way!")
                    print("yol yok!")

    def auto_start_stop(self):
        if self.vehicle_stop and traci.vehicle.getSpeed(self.vehicle_id) > 0:
            traci.vehicle.setSpeed(self.vehicle_id, 0)
        else:
            lane_id = traci.vehicle.getLaneID(self.vehicle_id)
            if traci.vehicle.getRoadID(self.vehicle_id) == traci.vehicle.getRoute(self.vehicle_id)[-1]:
                edge_length = traci.lane.getLength(lane_id)
                vehicle_position = traci.vehicle.getLanePosition(self.vehicle_id)
                if edge_length - vehicle_position <= 35 and traci.vehicle.getSpeed(self.vehicle_id) > 0:
                    self.vehicle_stop = True
                    print("stop")
                    # time.sleep(3)
                    # self.set_route_by_instruction("sol")
            elif traci.vehicle.getSpeed(self.vehicle_id) < 10:
                traci.vehicle.setSpeed(self.vehicle_id, 10)

    def run(self):
        aa = traci.start(self.sumoCmd)
        traci.gui.setSchema('View #0', 'real world')
        traci.gui.setZoom('View #0', 750)
        traci.gui.setOffset('View #0', 2000, 2000)

        while True:
            try:
                traci.simulationStep()
            except Exception as e:
                print("step error:", e)

            time.sleep(0.33)
            if not self.vehicle_id:
                self.vehicle_id = traci.vehicle.getIDList()[0]
                traci.gui.trackVehicle('View #0', self.vehicle_id)
                traci.vehicle.setLength(self.vehicle_id, 9)
                traci.vehicle.setWidth(self.vehicle_id, 4.5)

            if len(traci.vehicle.getIDList()) > 0:
                self.auto_start_stop()

            #with self.lock:
            if (self.runInstruction):
                self.set_route_by_instruction(self.instruction)
                self.instruction = ""
                self.runInstruction = False

            if(self.stop):
                break


        traci.close()

# s1 = Sumo()
# s1.run()

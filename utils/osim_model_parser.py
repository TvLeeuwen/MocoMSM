"""
Parse .osim (.xml) file for jointset and forceset elements.
"""

# Imports ---------------------------------------------------------------------
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
from lxml import etree


# Parse args ------------------------------------------------------------------
def parse_arguments():
    """
    Parse CLI arguments
    """
    parser = argparse.ArgumentParser(
        description="Generate an initial mesh for mmg based mesh adaptation",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help='Use switches followed by "=" to use CLI file autocomplete, example "-i="',
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Path to input .osim model",
        required=True,
    )
    return parser.parse_args()


# Defs ------------------------------------------------------------------------

# def parse_data(element):
#     print(f"- {element.tag}")
#     if element.attrib:
#         print(f"  - {element.attrib}")
#     if element.text and element.text.strip():
#         print(f"    {element.text.strip()}")
#     for child in element:
#         print(" -", end="")
#         parse_data(child)


# Main ------------------------------------------------------------------------
def parse_model(osim):
    """
    Specific order o
    """
    states = ["time"]
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(osim, parser)
    root = tree.getroot()

    # Jointset values
    joint_set = root.findall("Model/JointSet/objects/")
    joints = [joint for joint in joint_set if joint.tag != "WeldJoint"]
    for joint in joints:
        joint_name = joint.attrib.get("name", "Unnamed Joint")
        coordinates = joint.find("coordinates")
        if coordinates is not None:
            for coordinate in coordinates.findall("Coordinate"):
                coord_name = coordinate.attrib.get("name")
                states.append(f"/jointset/{joint_name}/{coord_name}/value")

    # Jointset speed
    joint_set = root.findall("Model/JointSet/objects/")
    joints = [joint for joint in joint_set if joint.tag != "WeldJoint"]
    for joint in joints:
        joint_name = joint.attrib.get("name", "Unnamed Joint")
        coordinates = joint.find("coordinates")
        if coordinates is not None:
            for coordinate in coordinates.findall("Coordinate"):
                coord_name = coordinate.attrib.get("name")
                states.append(f"/jointset/{joint_name}/{coord_name}/speed")

    # Force activation / normalized tendon force
    force_set = root.findall("Model/ForceSet/objects/")
    forces = [force for force in force_set]
    for force in forces:
        if "DeGroote" in force.tag:
            states.append(f"/forceset/{force.attrib.get('name')}/activation")
            states.append(
                f"/forceset/{force.attrib.get('name')}/normalized_tendon_force"
            )

    # Force
    force_set = root.findall("Model/ForceSet/objects/")
    forces = [force for force in force_set]
    for force in forces:
        if "DeGroote" in force.tag:
            states.append(f"/forceset/{force.attrib.get('name')}")

    # Jointset accel
    joint_set = root.findall("Model/JointSet/objects/")
    joints = [joint for joint in joint_set if joint.tag != "WeldJoint"]
    for joint in joints:
        joint_name = joint.attrib.get("name", "Unnamed Joint")
        coordinates = joint.find("coordinates")
        if coordinates is not None:
            for coordinate in coordinates.findall("Coordinate"):
                coord_name = coordinate.attrib.get("name")
                states.append(f"/jointset/{joint_name}/{coord_name}/accel")

    # Force implicitderiv_normalized_tendon_force
    force_set = root.findall("Model/ForceSet/objects/")
    forces = [force for force in force_set]
    for force in forces:
        if "DeGroote" in force.tag:
            states.append(
                f"/forceset/{force.attrib.get('name')}/implicitderiv_normalized_tendon_force"
            )

    return states

if __name__ == "__main__":
    args = parse_arguments()

    states = parse_model(Path(args.input))
    [print(state) for state in states]
    print(f"Total states: {len(states)}")

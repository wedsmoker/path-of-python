import json
from core.utils import load_json

class PassiveNode:
    """Represents a single node in the passive skill tree."""

    def __init__(self, node_id, name, description, effects, prerequisites=None, position=None):
        self.node_id = node_id
        self.name = name
        self.description = description
        self.effects = effects  # Dictionary of effect types and their values
        self.prerequisites = prerequisites or []  # List of node IDs that must be activated first
        self.position = position or (0, 0)  # (x, y) position in the tree
        self.is_activated = False

    def activate(self):
        """Activate this node."""
        self.is_activated = True

    def deactivate(self):
        """Deactivate this node."""
        self.is_activated = False

    def get_effects(self):
        """Return the effects of this node if activated."""
        if self.is_activated:
            return self.effects
        return {}

class PassiveTree:
    """Manages the passive skill tree for a character."""

    def __init__(self, tree_data_path):
        self.tree_data_path = tree_data_path
        self.nodes = {}
        self.activated_nodes = set()
        self.load_tree_data()

    def load_tree_data(self):
        """Load the passive skill tree data from a JSON file."""
        tree_data = load_json(self.tree_data_path)
        if tree_data:
            for node_data in tree_data.get('nodes', []):
                node = PassiveNode(
                    node_id=node_data['id'],
                    name=node_data['name'],
                    description=node_data['description'],
                    effects=node_data['effects'],
                    prerequisites=node_data.get('prerequisites', []),
                    position=node_data.get('position', (0, 0))
                )
                self.nodes[node_data['id']] = node

    def activate_node(self, node_id):
        """Activate a node in the passive skill tree."""
        if node_id in self.nodes:
            node = self.nodes[node_id]

            # Check prerequisites
            if all(prereq in self.activated_nodes for prereq in node.prerequisites):
                node.activate()
                self.activated_nodes.add(node_id)
                return True
            else:
                print(f"Cannot activate node {node_id}: Prerequisites not met.")
                return False
        else:
            print(f"Node {node_id} not found.")
            return False

    def deactivate_node(self, node_id):
        """Deactivate a node in the passive skill tree."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.deactivate()
            self.activated_nodes.discard(node_id)
        else:
            print(f"Node {node_id} not found.")

    def get_cumulative_effects(self):
        """Calculate the cumulative effects of all activated nodes."""
        cumulative_effects = {}

        for node in self.nodes.values():
            if node.is_activated:
                for effect_type, value in node.effects.items():
                    if effect_type in cumulative_effects:
                        cumulative_effects[effect_type] += value
                    else:
                        cumulative_effects[effect_type] = value

        return cumulative_effects

    def get_node_by_position(self, position):
        """Get a node by its position in the tree."""
        for node in self.nodes.values():
            if node.position == position:
                return node
        return None
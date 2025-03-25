import pygame
import json

class InputHandling:
    def __init__(self, key_bindings_file=None, actions=None, mouse_bindings_file=None):
        """
        key_bindings_file: path to the JSON file with key-action mappings.
        actions: a dictionary mapping action names (strings) to callables.
        mouse_bindings_file: (Optional) path to a JSON file with mouse button-action mappings.
        """
        self.actions = actions
        self.key_bindings = self.load_key_bindings(key_bindings_file)
        self.mouse_bindings = self.load_mouse_bindings(mouse_bindings_file) if mouse_bindings_file else {}

    def load_key_bindings(self, filename):
        with open(filename, 'r') as f:
            bindings = json.load(f)
        converted = {}
        for key_str, action in bindings.items():
            # Only process keys that start with "K_"
            if key_str.startswith("K_"):
                key_const = getattr(pygame, key_str, None)
                if key_const is not None:
                    converted[key_const] = action
                else:
                    print(f"Warning: {key_str} is not a valid pygame key constant.")
        return converted

    def load_mouse_bindings(self, filename):
        with open(filename, 'r') as f:
            bindings = json.load(f)
        converted = {}
        for key_str, action in bindings.items():
            # Convert names like "MOUSE_LEFT" to a button number.
            if key_str == "MOUSE_LEFT":
                converted[1] = action
            elif key_str == "MOUSE_MIDDLE":
                converted[2] = action
            elif key_str == "MOUSE_RIGHT":
                converted[3] = action
            else:
                try:
                    button = int(key_str)
                    converted[button] = action
                except ValueError:
                    print(f"Warning: {key_str} is not a valid mouse button key.")
        return converted

    def run(self, event):
        if event.type == pygame.KEYDOWN:
            action_name = self.key_bindings.get(event.key)
            if action_name:
                action_function = self.actions.get(action_name)
                if action_function:
                    action_function()
                else:
                    print(f"No action function defined for: {action_name}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            action_name = self.mouse_bindings.get(event.button)
            if action_name:
                action_function = self.actions.get(action_name)
                if action_function:
                    action_function()
                else:
                    print(f"No action function defined for: {action_name}")
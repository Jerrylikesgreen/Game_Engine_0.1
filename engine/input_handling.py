import pygame
import json

class InputHandling:
    def __init__(self, key_bindings_file, actions):
        """
        key_bindings_file: path to the JSON file with key-action mappings.
        actions: a dictionary mapping action names (strings) to callables.
        """
        self.actions = actions
        self.key_bindings = self.load_key_bindings(key_bindings_file)

    def load_key_bindings(self, filename):
        with open(filename, 'r') as f:
            bindings = json.load(f)
        converted = {}
        for key_str, action in bindings.items():
            key_const = getattr(pygame, key_str, None)
            if key_const is not None:
                converted[key_const] = action
            else:
                print(f"Warning: {key_str} is not a valid pygame key constant.")
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

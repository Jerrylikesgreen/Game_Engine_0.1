
''' This module is responsible for managing the scenes of the game. It contains the SceneManager class, which is responsible for adding scenes, changing scenes, updating scenes, and drawing scenes. '''
class SceneManager:
    def __init__(self, game):
        self.game = game
        self.scenes = {}
        self.current_scene = None
        
    def add_scene(self, scene_name, scene):
        self.scenes[scene_name] = scene
        
    def change_scene(self, scene_name):
        self.current_scene = self.scenes[scene_name]
        self.current_scene.start()
        
    def update(self):
        self.current_scene.update()
        def draw(self):

            self.current_scene.draw()
            
    def handle_events(self):
        self.current_scene.handle_events()
        
    def get_scene(self, scene_name):
        return self.scenes[scene_name]
      

class GamePhase:
    def __init__(self, game):
        self.game = game

    def execute(self):
        raise NotImplementedError("Subclasses should implement this method.")

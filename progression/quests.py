import json
from core.utils import load_json

class Quest:
    """Represents a single quest in the game."""

    def __init__(self, quest_id, title, description, objectives, rewards, is_main_quest=False):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives  # List of objective dictionaries
        self.rewards = rewards  # Dictionary of reward types and amounts
        self.is_main_quest = is_main_quest
        self.is_completed = False
        self.completed_objectives = 0

    def update(self):
        """Update the quest's progress."""
        completed = True
        for objective in self.objectives:
            if not objective['completed']:
                completed = False
                break

        if completed and not self.is_completed:
            self.complete()

    def complete(self):
        """Mark the quest as completed."""
        self.is_completed = True
        print(f"Quest completed: {self.title}")

    def get_progress(self):
        """Get the progress of the quest as a percentage."""
        if len(self.objectives) > 0:
            return (self.completed_objectives / len(self.objectives)) * 100
        return 0

class QuestManager:
    """Manages all quests in the game."""

    def __init__(self, quest_data_path):
        self.quest_data_path = quest_data_path
        self.quests = {}
        self.active_quests = []
        self.completed_quests = []
        self.load_quest_data()

    def load_quest_data(self):
        """Load quest data from a JSON file."""
        quest_data = load_json(self.quest_data_path)
        if quest_data:
            for quest_info in quest_data.get('quests', []):
                quest = Quest(
                    quest_id=quest_info['id'],
                    title=quest_info['name'], # Changed from 'title' to 'name'
                    description=quest_info['description'],
                    objectives=quest_info['objectives'],
                    rewards=quest_info['rewards'],
                    is_main_quest=quest_info.get('is_main_quest', False)
                )
                self.quests[quest_info['id']] = quest

    def start_quest(self, quest_id):
        """Start a quest."""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest not in self.active_quests and not quest.is_completed:
                self.active_quests.append(quest)
                print(f"Quest started: {quest.title}")
            else:
                print(f"Quest already active or completed: {quest.title}")
        else:
            print(f"Quest not found: {quest_id}")

    def complete_objective(self, quest_id, objective_index):
        """Mark an objective as completed."""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if objective_index < len(quest.objectives):
                quest.objectives[objective_index]['completed'] = True
                quest.completed_objectives += 1
                quest.update()
            else:
                print(f"Objective index out of range: {objective_index}")
        else:
            print(f"Quest not found: {quest_id}")

    def get_active_quests(self):
        """Get all active quests."""
        return self.active_quests

    def get_completed_quests(self):
        """Get all completed quests."""
        return self.completed_quests

    def get_quest_by_id(self, quest_id):
        """Get a quest by its ID."""
        return self.quests.get(quest_id, None)
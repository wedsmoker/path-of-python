import json
from core.utils import load_json

class Quest:
    """Represents a single quest in the game."""

    def __init__(self, quest_id, title, description, objectives, rewards, is_main_quest=False, is_completed=False, is_unlocked=False, tilemap_scene_name=None):
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives  # List of objective dictionaries
        self.rewards = rewards  # Dictionary of reward types and amounts
        self.is_main_quest = is_main_quest
        self.is_completed = is_completed # Initialize from data
        self.is_unlocked = is_unlocked # Initialize from data
        self.tilemap_scene_name = tilemap_scene_name
        self.completed_objectives = 0
        # Recalculate completed objectives if quest is already completed
        if self.is_completed:
            self.completed_objectives = len(self.objectives)
        else:
            for obj in self.objectives:
                if obj.get('completed', False):
                    self.completed_objectives += 1

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
        # Logic to unlock next quest will be handled by QuestManager

    def get_progress(self):
        """Get the progress of the quest as a percentage."""
        if len(self.objectives) > 0:
            return (self.completed_objectives / len(self.objectives)) * 100
        return 0

class QuestManager:
    """Manages all quests in the game."""

    def __init__(self, quest_data_path):
        self.quest_data_path = quest_data_path
        self.quests = {} # Dictionary of all quests by ID
        self.active_quests = [] # List of active quest objects
        self.completed_quests = [] # List of completed quest objects
        self.load_quest_data()

    def load_quest_data(self):
        """Load quest data from a JSON file."""
        quest_data = load_json(self.quest_data_path)
        if quest_data and 'quests' in quest_data:
            for quest_info in quest_data['quests']: # Access 'quests' key directly
                quest = Quest(
                    quest_id=quest_info['id'],
                    title=quest_info['name'],
                    description=quest_info['description'],
                    objectives=quest_info.get('objectives', []), # Ensure objectives exist
                    rewards=quest_info.get('rewards', {}), # Ensure rewards exist
                    is_main_quest=quest_info.get('is_main_quest', False),
                    is_completed=quest_info.get('is_completed', False), # Load is_completed
                    is_unlocked=quest_info.get('is_unlocked', False), # Load is_unlocked
                    tilemap_scene_name=quest_info.get('tilemap_scene_name')
                )
                self.quests[quest_info['id']] = quest
                if quest.is_completed:
                    self.completed_quests.append(quest)
                # Active quests are typically started by player action, not loaded as active initially
                # unless there's a save state mechanism. For now, only load completed state.

    def start_quest(self, quest_id):
        """Start a quest."""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest.is_unlocked and not quest.is_completed and quest not in self.active_quests:
                self.active_quests.append(quest)
                print(f"Quest started: {quest.title}")
            else:
                print(f"Quest cannot be started: {quest.title} (Unlocked: {quest.is_unlocked}, Completed: {quest.is_completed}, Active: {quest in self.active_quests})")
        else:
            print(f"Quest not found: {quest_id}")

    def complete_objective(self, quest_id, objective_index):
        """Mark an objective as completed."""
        if quest_id in self.quests:
            quest = self.quests[quest_id]
            if quest in self.active_quests and objective_index < len(quest.objectives):
                if not quest.objectives[objective_index].get('completed', False):
                    quest.objectives[objective_index]['completed'] = True
                    quest.completed_objectives += 1
                    quest.update()
                    if quest.is_completed:
                        self.completed_quests.append(quest)
                        if quest in self.active_quests:
                            self.active_quests.remove(quest)
                        self._unlock_next_quest(quest.quest_id) # Unlock next quest
                else:
                    print(f"Objective already completed: {quest.title} - Objective {objective_index}")
            else:
                print(f"Quest not active or objective index out of range: {quest_id} - Objective {objective_index}")
        else:
            print(f"Quest not found: {quest_id}")

    def _unlock_next_quest(self, completed_quest_id):
        """Unlocks the next sequential quest."""
        quest_ids = list(self.quests.keys())
        try:
            current_quest_index = quest_ids.index(completed_quest_id)
            if current_quest_index + 1 < len(quest_ids):
                next_quest_id = quest_ids[current_quest_index + 1]
                next_quest = self.quests[next_quest_id]
                if not next_quest.is_unlocked:
                    next_quest.is_unlocked = True
                    print(f"Quest unlocked: {next_quest.title}")
        except ValueError:
            print(f"Completed quest ID {completed_quest_id} not found in quest list.")

    def get_active_quests(self):
        """Get all active quests."""
        return self.active_quests

    def get_completed_quests(self):
        """Get all completed quests."""
        return self.completed_quests

    def get_quest_by_id(self, quest_id):
        """Get a quest by its ID."""
        return self.quests.get(quest_id, None)

    def get_unlocked_quests(self):
        """Get all quests that are unlocked (including completed ones)."""
        return [quest for quest in self.quests.values() if quest.is_unlocked]
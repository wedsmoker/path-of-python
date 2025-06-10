class ExperienceSystem:
    """Manages experience points, leveling, and skill point allocation."""

    def __init__(self, starting_level=1, starting_xp=0):
        self.level = starting_level
        self.xp = starting_xp
        self.xp_to_next_level = self.calculate_xp_for_level(self.level + 1)
        self.skill_points = 0
        self.max_skill_points = 100  # Maximum skill points a character can have

    def gain_xp(self, xp_amount):
        """Add experience points to the character."""
        self.xp += xp_amount
        while self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Handle leveling up."""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = self.calculate_xp_for_level(self.level + 1)
        self.skill_points += 1  # Gain 1 skill point per level
        print(f"Level up! Now level {self.level} with {self.skill_points} skill points.")

    def allocate_skill_point(self):
        """Allocate a skill point."""
        if self.skill_points > 0:
            self.skill_points -= 1
            return True
        else:
            print("No skill points available to allocate.")
            return False

    def calculate_xp_for_level(self, level):
        """Calculate the XP required for a given level using a formula."""
        # Example formula: XP = base * level^2
        base_xp = 100
        return base_xp * (level ** 2)

    def get_xp_progress(self):
        """Get the current XP progress towards the next level as a percentage."""
        if self.xp_to_next_level > 0:
            return (self.xp / self.xp_to_next_level) * 100
        return 0

    def get_status(self):
        """Get the current status of the experience system."""
        return {
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "skill_points": self.skill_points,
            "xp_progress": self.get_xp_progress()
        }
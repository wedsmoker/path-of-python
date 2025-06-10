class WorldState:
    """Manages the global state of the game world."""

    def __init__(self):
        self.player = None  # Will hold the Player object
        self.current_zone = None  # Current zone the player is in
        self.active_quests = []  # List of active quests
        self.completed_quests = []  # List of completed quests
        self.discovered_areas = set()  # Set of discovered area IDs
        self.time_of_day = 0  # Time of day in seconds (0-86400 for a full day)
        self.weather = "clear"  # Current weather condition
        self.day_count = 1  # Current day count
        self.global_events = []  # List of global events that affect the world

    def set_player(self, player):
        """Set the player object."""
        self.player = player

    def set_current_zone(self, zone):
        """Set the current zone."""
        self.current_zone = zone

    def add_active_quest(self, quest):
        """Add an active quest."""
        if quest not in self.active_quests:
            self.active_quests.append(quest)

    def complete_quest(self, quest):
        """Complete a quest."""
        if quest in self.active_quests:
            self.active_quests.remove(quest)
            self.completed_quests.append(quest)
            # Handle quest rewards here

    def discover_area(self, area_id):
        """Mark an area as discovered."""
        self.discovered_areas.add(area_id)

    def is_area_discovered(self, area_id):
        """Check if an area has been discovered."""
        return area_id in self.discovered_areas

    def update_time_of_day(self, dt):
        """Update the time of day."""
        self.time_of_day = (self.time_of_day + dt) % 86400  # 86400 seconds in a day

    def get_time_of_day(self):
        """Get the current time of day as a string."""
        hours = int(self.time_of_day // 3600)
        minutes = int((self.time_of_day % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"

    def set_weather(self, weather_condition):
        """Set the current weather condition."""
        self.weather = weather_condition

    def advance_day(self):
        """Advance to the next day."""
        self.day_count += 1
        # Reset time of day
        self.time_of_day = 0
        # Handle daily events or resets here

    def add_global_event(self, event):
        """Add a global event that affects the world."""
        self.global_events.append(event)

    def process_global_events(self):
        """Process all global events."""
        for event in self.global_events:
            # Handle each event
            pass
        # Clear processed events
        self.global_events = []

    def get_status(self):
        """Get the current status of the world state."""
        return {
            "player": self.player,
            "current_zone": self.current_zone,
            "active_quests": self.active_quests,
            "completed_quests": self.completed_quests,
            "discovered_areas": self.discovered_areas,
            "time_of_day": self.get_time_of_day(),
            "weather": self.weather,
            "day_count": self.day_count
        }
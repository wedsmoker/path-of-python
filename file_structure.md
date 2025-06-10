# Project File Structure (Excluding PNGs)

```
.
├── GAME_DESIGN.md
├── main.py
├── Path of Python.code-workspace
├── please.txt
├── skill_activation_plan.md
├── spawntown_enhancement_plan.md
├── combat/
├── config/
├── core/
│   ├── base_gameplay_scene.py
│   ├── game_engine.py
│   ├── input_handler.py
│   ├── pathfinding.py
│   ├── scene_manager.py
│   └── utils.py
├── data/
│   ├── dialogue.json
│   ├── enemies.json
│   ├── items.json
│   ├── passive_tree.json
│   ├── quests.json
│   ├── skills.json
│   └── zone_data.json
├── entities/
│   ├── effects.py
│   ├── enemy.py
│   ├── npc.py
│   ├── player_sprites.py
│   ├── player.py
│   └── projectile.py
├── graphics/
│   ├── __init__.py
│   ├── LICENSE.txt
│   ├── README.txt
│   ├── effect/
│   ├── player/
│   │   ├── ench/
│   │   └── halo/
│   ├── spells/
│   │   ├── air/
│   │   ├── conjuration/
│   │   ├── disciplines/
│   │   ├── divination/
│   │   ├── earth/
│   │   ├── enchantment/
│   │   ├── fire/
│   │   ├── ice/
│   │   ├── necromancy/
│   │   ├── poison/
│   │   ├── summoning/
│   │   ├── translocation/
│   │   └── transmutation/
│   ├── sprites/
│   │   └── __init__.py
│   ├── UNUSED/
│   │   ├── armour/
│   │   ├── potions/
│   │   ├── rings/
│   │   ├── spells/
│   │   └── weapons/
│   └── utility/
│       ├── Deleted List.txt
│       ├── Filtered List.txt
│       ├── licenseFinder.py
│       ├── Raw List.txt
│       └── README.txt
├── items/
│   ├── armor.py
│   ├── gem.py
│   ├── item.py
│   ├── loot_generator.py
│   └── weapon.py
├── progression/
│   ├── classes.py
│   ├── experience.py
│   ├── passive_tree.py
│   └── quests.py
├── saves/
│   └── placeholder.txt
├── tests/
│   ├── test_combat.py
│   └── test_inventory.py
├── ui/
└── world/
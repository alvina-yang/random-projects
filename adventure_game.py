import random
import time
import sys
import os
from typing import List, Dict, Optional, Tuple


class Item:
    def __init__(self, name: str, description: str, weight: float = 1.0, value: int = 0):
        self.name = name
        self.description = description
        self.weight = weight
        self.value = value
    
    def __str__(self) -> str:
        return f"{self.name} ({self.weight} kg, {self.value} gold)"


class Weapon(Item):
    def __init__(self, name: str, description: str, damage: int, weight: float = 2.0, value: int = 10):
        super().__init__(name, description, weight, value)
        self.damage = damage
    
    def __str__(self) -> str:
        return f"{self.name} - Damage: {self.damage} ({self.weight} kg, {self.value} gold)"


class Potion(Item):
    def __init__(self, name: str, description: str, effect_value: int, effect_type: str, weight: float = 0.5, value: int = 15):
        super().__init__(name, description, weight, value)
        self.effect_value = effect_value
        self.effect_type = effect_type  # "health", "strength", etc.
    
    def __str__(self) -> str:
        return f"{self.name} - {self.effect_type.capitalize()} +{self.effect_value} ({self.weight} kg, {self.value} gold)"


class Creature:
    def __init__(self, name: str, description: str, health: int, strength: int):
        self.name = name
        self.description = description
        self.health = health
        self.max_health = health
        self.strength = strength
        self.is_alive = True
    
    def take_damage(self, damage: int) -> None:
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.is_alive = False
    
    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)
    
    def __str__(self) -> str:
        return f"{self.name} - Health: {self.health}/{self.max_health}, Strength: {self.strength}"


class Player(Creature):
    def __init__(self, name: str, health: int = 100, strength: int = 10):
        super().__init__(name, f"The brave adventurer {name}", health, strength)
        self.inventory: List[Item] = []
        self.equipped_weapon: Optional[Weapon] = None
        self.gold = 50
        self.experience = 0
        self.level = 1
    
    def add_to_inventory(self, item: Item) -> None:
        self.inventory.append(item)
        print(f"Added {item.name} to your inventory.")
    
    def remove_from_inventory(self, item: Item) -> None:
        if item in self.inventory:
            self.inventory.remove(item)
    
    def equip_weapon(self, weapon: Weapon) -> None:
        if weapon in self.inventory:
            self.equipped_weapon = weapon
            print(f"Equipped {weapon.name}.")
        else:
            print("You don't have that weapon in your inventory.")
    
    def attack(self, target: Creature) -> int:
        damage = self.strength
        if self.equipped_weapon:
            damage += self.equipped_weapon.damage
        
        # Add some randomness to damage
        damage = int(damage * random.uniform(0.8, 1.2))
        
        target.take_damage(damage)
        return damage
    
    def use_potion(self, potion: Potion) -> bool:
        if potion not in self.inventory:
            print("You don't have that potion in your inventory.")
            return False
        
        if potion.effect_type == "health":
            self.heal(potion.effect_value)
            print(f"You used {potion.name} and restored {potion.effect_value} health.")
        elif potion.effect_type == "strength":
            self.strength += potion.effect_value
            print(f"You used {potion.name} and gained {potion.effect_value} strength.")
        
        self.remove_from_inventory(potion)
        return True
    
    def gain_experience(self, amount: int) -> None:
        self.experience += amount
        print(f"Gained {amount} experience points!")
        
        # Check for level up (simple formula: 100 * current_level)
        if self.experience >= 100 * self.level:
            self.level_up()
    
    def level_up(self) -> None:
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.strength += 5
        print(f"\n✨ LEVEL UP! ✨\nYou are now level {self.level}!")
        print(f"Max Health increased to {self.max_health}")
        print(f"Strength increased to {self.strength}")
    
    def __str__(self) -> str:
        status = super().__str__()
        return f"{status}, Level: {self.level}, XP: {self.experience}, Gold: {self.gold}"


class Enemy(Creature):
    def __init__(self, name: str, description: str, health: int, strength: int, 
                 loot: List[Item] = None, experience_value: int = 10, gold_value: int = 5):
        super().__init__(name, description, health, strength)
        self.loot = loot if loot is not None else []
        self.experience_value = experience_value
        self.gold_value = gold_value
    
    def attack(self, target: Player) -> int:
        damage = int(self.strength * random.uniform(0.8, 1.2))
        target.take_damage(damage)
        return damage


class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.items: List[Item] = []
        self.enemies: List[Enemy] = []
        self.exits: Dict[str, 'Room'] = {}  # direction -> room
    
    def add_exit(self, direction: str, room: 'Room') -> None:
        self.exits[direction] = room
    
    def add_item(self, item: Item) -> None:
        self.items.append(item)
    
    def remove_item(self, item: Item) -> None:
        if item in self.items:
            self.items.remove(item)
    
    def add_enemy(self, enemy: Enemy) -> None:
        self.enemies.append(enemy)
    
    def remove_enemy(self, enemy: Enemy) -> None:
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def get_living_enemies(self) -> List[Enemy]:
        return [enemy for enemy in self.enemies if enemy.is_alive]
    
    def describe(self) -> str:
        description = f"\n{self.name}\n{'=' * len(self.name)}\n{self.description}\n"
        
        if self.items:
            description += "\nItems in this room:\n"
            for item in self.items:
                description += f"- {item}\n"
        
        enemies = self.get_living_enemies()
        if enemies:
            description += "\nEnemies in this room:\n"
            for enemy in enemies:
                description += f"- {enemy.name}: {enemy.health}/{enemy.max_health} HP\n"
        
        if self.exits:
            description += "\nExits:\n"
            for direction, room in self.exits.items():
                description += f"- {direction}: {room.name}\n"
        
        return description


class Game:
    def __init__(self):
        self.player = None
        self.current_room = None
        self.rooms = []
        self.running = False
    
    def initialize_game(self) -> None:
        # Create player
        player_name = input("Enter your character's name: ")
        self.player = Player(player_name)
        
        # Create items
        sword = Weapon("Rusty Sword", "An old sword with some rust spots.", 5, 3.0, 10)
        dagger = Weapon("Steel Dagger", "A small but sharp dagger.", 3, 1.0, 8)
        health_potion = Potion("Health Potion", "A red potion that restores health.", 30, "health", 0.5, 15)
        strength_potion = Potion("Strength Elixir", "A glowing blue potion that increases strength.", 3, "strength", 0.5, 25)
        
        # Give player starting equipment
        self.player.add_to_inventory(sword)
        self.player.add_to_inventory(health_potion)
        self.player.equip_weapon(sword)
        
        # Create rooms
        entrance = Room("Cave Entrance", "A dimly lit entrance to a mysterious cave. Water drips from the ceiling.")
        main_hall = Room("Main Hall", "A large cavern with ancient pillars. Footprints can be seen in the dust.")
        treasure_room = Room("Treasure Chamber", "A small room filled with chests and valuable-looking items.")
        monster_den = Room("Monster Den", "A foul-smelling chamber where creatures lurk in the shadows.")
        exit_tunnel = Room("Exit Tunnel", "A narrow passage that seems to lead outside.")
        
        # Connect rooms
        entrance.add_exit("north", main_hall)
        
        main_hall.add_exit("south", entrance)
        main_hall.add_exit("east", treasure_room)
        main_hall.add_exit("west", monster_den)
        main_hall.add_exit("north", exit_tunnel)
        
        treasure_room.add_exit("west", main_hall)
        
        monster_den.add_exit("east", main_hall)
        
        exit_tunnel.add_exit("south", main_hall)
        
        # Add items to rooms
        entrance.add_item(dagger)
        treasure_room.add_item(strength_potion)
        treasure_room.add_item(health_potion)
        
        # Create enemies
        goblin = Enemy("Goblin", "A small, green creature with sharp teeth.", 20, 5, 
                      [Item("Goblin Ear", "A pointy ear from a goblin.", 0.1, 2)], 15, 5)
        
        troll = Enemy("Cave Troll", "A large, hulking creature with gray skin.", 50, 8,
                     [Weapon("Troll Club", "A heavy wooden club.", 7, 5.0, 15)], 30, 15)
        
        # Add enemies to rooms
        monster_den.add_enemy(goblin)
        monster_den.add_enemy(troll)
        
        # Set current room
        self.current_room = entrance
        self.rooms = [entrance, main_hall, treasure_room, monster_den, exit_tunnel]
    
    def display_help(self) -> None:
        print("\nAvailable Commands:")
        print("  look - Look around the room")
        print("  go [direction] - Move in a direction (north, south, east, west)")
        print("  take [item] - Pick up an item")
        print("  inventory - Check your inventory")
        print("  equip [weapon] - Equip a weapon from your inventory")
        print("  use [item] - Use an item from your inventory")
        print("  attack [enemy] - Attack an enemy")
        print("  stats - Display your character stats")
        print("  help - Display this help message")
        print("  quit - Exit the game")
    
    def handle_combat(self, enemy_name: str) -> None:
        # Find the enemy in the current room
        enemy = None
        for e in self.current_room.get_living_enemies():
            if e.name.lower() == enemy_name.lower():
                enemy = e
                break
        
        if not enemy:
            print(f"There is no living enemy called '{enemy_name}' here.")
            return
        
        # Player attacks first
        damage_dealt = self.player.attack(enemy)
        print(f"You attack the {enemy.name} with your {self.player.equipped_weapon.name if self.player.equipped_weapon else 'fists'}.")
        print(f"You deal {damage_dealt} damage to the {enemy.name}.")
        
        # Check if enemy is defeated
        if not enemy.is_alive:
            print(f"You have defeated the {enemy.name}!")
            
            # Give player rewards
            self.player.gold += enemy.gold_value
            print(f"You found {enemy.gold_value} gold.")
            
            self.player.gain_experience(enemy.experience_value)
            
            # Add loot to the room
            for item in enemy.loot:
                self.current_room.add_item(item)
                print(f"The {enemy.name} dropped: {item.name}")
            
            return
        
        # Enemy counterattacks
        damage_taken = enemy.attack(self.player)
        print(f"The {enemy.name} attacks you and deals {damage_taken} damage!")
        
        # Check if player is defeated
        if not self.player.is_alive:
            print("\nYou have been defeated! Game over.")
            self.running = False
            return
        
        # Show both health values
        print(f"Your health: {self.player.health}/{self.player.max_health}")
        print(f"{enemy.name}'s health: {enemy.health}/{enemy.max_health}")
    
    def run(self) -> None:
        self.initialize_game()
        self.running = True
        
        # Introduction
        print("\n" + "=" * 60)
        print("WELCOME TO THE CAVE ADVENTURE!")
        print("=" * 60)
        print(f"You, {self.player.name}, stand at the entrance of a mysterious cave.")
        print("Rumors say there's treasure inside, but also dangerous creatures.")
        print("Type 'help' for a list of commands.")
        print("=" * 60 + "\n")
        
        # Main game loop
        while self.running:
            # Print current room if changed
            print(self.current_room.describe())
            
            # Get player input
            command = input("\nWhat do you want to do? ").strip().lower()
            
            # Process command
            if command == "quit":
                confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
                if confirm == "y":
                    print("Thanks for playing!")
                    self.running = False
            
            elif command == "help":
                self.display_help()
            
            elif command == "look":
                print(self.current_room.describe())
            
            elif command.startswith("go "):
                direction = command[3:].strip()
                if direction in self.current_room.exits:
                    self.current_room = self.current_room.exits[direction]
                    print(f"You go {direction}.")
                else:
                    print(f"There is no exit in the {direction} direction.")
            
            elif command.startswith("take "):
                item_name = command[5:].strip()
                for item in self.current_room.items:
                    if item.name.lower() == item_name.lower():
                        self.player.add_to_inventory(item)
                        self.current_room.remove_item(item)
                        break
                else:
                    print(f"There is no {item_name} here.")
            
            elif command == "inventory":
                if not self.player.inventory:
                    print("Your inventory is empty.")
                else:
                    print("\nInventory:")
                    for item in self.player.inventory:
                        if item == self.player.equipped_weapon:
                            print(f"- {item} (Equipped)")
                        else:
                            print(f"- {item}")
            
            elif command.startswith("equip "):
                weapon_name = command[6:].strip()
                for item in self.player.inventory:
                    if isinstance(item, Weapon) and item.name.lower() == weapon_name.lower():
                        self.player.equip_weapon(item)
                        break
                else:
                    print(f"You don't have a weapon called {weapon_name}.")
            
            elif command.startswith("use "):
                item_name = command[4:].strip()
                for item in self.player.inventory:
                    if item.name.lower() == item_name.lower():
                        if isinstance(item, Potion):
                            self.player.use_potion(item)
                        else:
                            print(f"You can't use {item.name} like that.")
                        break
                else:
                    print(f"You don't have an item called {item_name}.")
            
            elif command.startswith("attack "):
                enemy_name = command[7:].strip()
                self.handle_combat(enemy_name)
            
            elif command == "stats":
                print(f"\n{self.player}")
                if self.player.equipped_weapon:
                    print(f"Equipped weapon: {self.player.equipped_weapon}")
            
            else:
                print("I don't understand that command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Game terminated unexpectedly.") 
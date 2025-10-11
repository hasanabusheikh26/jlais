"""
PiDog action definitions for Gemini function calling.

Maps natural language commands to PiDog hardware actions.
Based on SunFounder PiDog official action library.
"""

# All available PiDog actions (verified from official examples)
PIDOG_ACTIONS = {
    # Basic Movement
    "sit": "Sit down on the ground",
    "stand": "Stand up on all four legs",
    "lie": "Lie down flat on the ground",
    
    # Walking (with step count)
    "forward": "Walk forward",
    "backward": "Walk backward",
    "turn_left": "Turn to the left",
    "turn_right": "Turn to the right",
    
    # Expressions & Sounds
    "bark": "Bark once (normal volume)",
    "bark_harder": "Bark loudly and aggressively",
    "wag_tail": "Wag tail happily",
    "pant": "Pant like a dog (breathing)",
    "howling": "Howl like a wolf",
    
    # Tricks
    "high_five": "Raise paw for high five",
    "handshake": "Offer paw for handshake",
    "push_up": "Do a push-up exercise",
    "stretch": "Stretch body forward",
    "scratch": "Scratch with back leg",
    "lick_hand": "Lick hand gesture",
    
    # Head Movements
    "nod": "Nod head up and down (yes)",
    "shake_head": "Shake head left and right (no)",
    "relax_neck": "Relax neck to comfortable position",
    
    # Emotions
    "think": "Thinking pose (head tilted)",
    "waiting": "Waiting/alert posture",
}


def get_pidog_functions():
    """
    Generate Gemini function calling schema for PiDog actions.
    
    This tells Gemini AI what physical actions it can trigger.
    
    Returns:
        list: Function definitions for Gemini
    """
    functions = []
    
    # Movement actions that accept step count
    movement_actions = ["forward", "backward", "turn_left", "turn_right"]
    
    for action, description in PIDOG_ACTIONS.items():
        if action in movement_actions:
            # Actions with step parameter
            functions.append({
                "name": action,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "integer",
                            "description": "Number of steps (1-10, default 3)",
                            "minimum": 1,
                            "maximum": 10,
                        },
                        "speed": {
                            "type": "integer",
                            "description": "Movement speed (1-100, default 80)",
                            "minimum": 1,
                            "maximum": 100,
                        }
                    },
                    "required": []
                }
            })
        else:
            # Standard actions with just speed
            functions.append({
                "name": action,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "speed": {
                            "type": "integer",
                            "description": "Movement speed (1-100, default 80)",
                            "minimum": 1,
                            "maximum": 100,
                        }
                    },
                    "required": []
                }
            })
    
    return functions


def list_all_actions():
    """Print all available actions (useful for reference)"""
    print("\n🐕 Available PiDog Actions:\n")
    print("=" * 60)
    
    categories = {
        "Basic Movement": ["sit", "stand", "lie"],
        "Walking": ["forward", "backward", "turn_left", "turn_right"],
        "Expressions & Sounds": ["bark", "bark_harder", "wag_tail", "pant", "howling"],
        "Tricks": ["high_five", "handshake", "push_up", "stretch", "scratch", "lick_hand"],
        "Head Movements": ["nod", "shake_head", "relax_neck"],
        "Emotions": ["think", "waiting"],
    }
    
    for category, actions in categories.items():
        print(f"\n{category}:")
        for action in actions:
            if action in PIDOG_ACTIONS:
                print(f"  • {action:15} - {PIDOG_ACTIONS[action]}")
    
    print("\n" + "=" * 60)
    print(f"Total: {len(PIDOG_ACTIONS)} actions available\n")


if __name__ == "__main__":
    # Print all actions when run directly
    list_all_actions()

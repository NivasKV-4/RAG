"""
Evaluation dataset for FlightLens

Each question entry:
{
    "id": str,
    "question": str,
    "ground_truth": str,
    "category": str,
    "difficulty": "easy" | "medium" | "hard",
    "requires_context": [] or ["metar"] or ["telemetry"] ...
}
"""

ALL_QUESTIONS = [
    # Emergency Procedures
    {
        "id": "E001",
        "question": "What are the steps for an engine fire during flight?",
        "ground_truth": (
            "Mixture - IDLE CUTOFF, Fuel Selector - OFF, "
            "Master Switch - OFF, Cabin Heat/Air - OFF, "
            "Airspeed - increase to extinguish fire, execute forced landing."
        ),
        "category": "emergency_procedure",
        "difficulty": "high",
        "requires_context": [],
    },
    {
        "id": "E002",
        "question": "How should a pilot respond to smoke in the cockpit?",
        "ground_truth": (
            "Establish best glide, turn off non-essential electrical equipment, "
            "identify and isolate the source, consider using fire extinguisher, "
            "land as soon as practicable."
        ),
        "category": "emergency_procedure",
        "difficulty": "medium",
        "requires_context": [],
    },
    {
        "id": "E003",
        "question": "What is the immediate action for rapid depressurization?",
        "ground_truth": (
            "Don oxygen masks, establish communication, initiate emergency descent "
            "to a safe altitude and level off, monitor passengers."
        ),
        "category": "emergency_procedure",
        "difficulty": "medium",
        "requires_context": [],
    },

    # Weather / METAR
    {
        "id": "W001",
        "question": "What does 'OVC003' in a METAR indicate?",
        "ground_truth": "Overcast cloud layer with base at 300 feet above ground level.",
        "category": "weather",
        "difficulty": "easy",
        "requires_context": [],
    },
    {
        "id": "W002",
        "question": "How is visibility reported in a METAR for 10 statute miles or more?",
        "ground_truth": "Visibility of 10 statute miles or more is reported as 10SM.",
        "category": "weather",
        "difficulty": "easy",
        "requires_context": [],
    },
    {
        "id": "W003",
        "question": "What does RMK AO2 mean in a METAR?",
        "ground_truth": "AO2 indicates an automated station with a precipitation sensor.",
        "category": "weather",
        "difficulty": "medium",
        "requires_context": [],
    },

    # Regulations / Rules
    {
        "id": "R001",
        "question": "What is the minimum safe altitude over a congested area?",
        "ground_truth": (
            "At least 1000 feet above the highest obstacle within a horizontal radius "
            "of 2000 feet of the aircraft."
        ),
        "category": "regulation",
        "difficulty": "medium",
        "requires_context": [],
    },
    {
        "id": "R002",
        "question": "What documents are required to be on board an aircraft (ARROW)?",
        "ground_truth": (
            "Airworthiness Certificate, Registration Certificate, "
            "Radio license (if required), Operating limitations, "
            "and Weight and balance data."
        ),
        "category": "regulation",
        "difficulty": "easy",
        "requires_context": [],
    },

    # Navigation / Performance
    {
        "id": "N001",
        "question": "What is maneuvering speed (Va)?",
        "ground_truth": (
            "The maximum speed at which full, abrupt control movements can be made "
            "without overstressing the aircraft; Va decreases with lower weight."
        ),
        "category": "performance",
        "difficulty": "medium",
        "requires_context": [],
    },
    {
        "id": "N002",
        "question": "How does bank angle affect stall speed?",
        "ground_truth": (
            "Stall speed increases with bank angle because the load factor increases; "
            "the steeper the bank, the higher the stall speed."
        ),
        "category": "performance",
        "difficulty": "medium",
        "requires_context": [],
    },

    # Context-dependent examples (for future METAR/telemetry-aware RAG)
    {
        "id": "C001",
        "question": "Given current METAR showing 2SM visibility and OVC004, can a VFR flight depart?",
        "ground_truth": (
            "With 2 statute miles visibility and overcast at 400 feet, "
            "conditions are below typical VFR minimums for most airspace; "
            "VFR departure is generally not allowed."
        ),
        "category": "weather",
        "difficulty": "high",
        "requires_context": ["metar"],
    },
    {
        "id": "C002",
        "question": "If the aircraft is at 5000 ft, 120 KIAS, and level, is this a stable cruise configuration?",
        "ground_truth": (
            "At 5000 feet and 120 knots indicated airspeed, level flight generally "
            "represents a stable cruise configuration if power and trim are set correctly."
        ),
        "category": "telemetry_reasoning",
        "difficulty": "medium",
        "requires_context": ["telemetry"],
    },
]

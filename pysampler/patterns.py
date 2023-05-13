import random

def prob_steps(probs: list[float], repeats: int = 0, duplicates: int = 0) -> list[int]:
    """Create and fill steps based on probabilities, 0..100
    
    Args:
        probs (list[int]): Probabilities (0-100)
        repeats (int): Number of times to iterate through probs
        duplicates (int): Number of times to extend the list

    Returns:
        list[bool]: Randomized steps
    """

    gates = []

    for _ in range(repeats + 1):
        for step in probs:
            chance_on = step * 0.01
            chance_off = 1 - chance_on
            gate = random.choices([1, 0], [chance_on, chance_off])[0]
            gates.append(gate)

    gates *= duplicates + 1
    
    return gates

def make_kick_steps(n_steps: int = 8, duplicates: int = 0, density: float = 0.25) -> list[int]:
    """Generate gate steps suitable for a kick drum
    Ensure that there is always a kick on 1st beat
    """
    gates = []

    # Fill steps
    for i in range(n_steps-1):
        if i == 0:
            # Always make gate on 1st step for kicks
            gates.append(1)
        else:
            gates.append(random.choices([0,1],[1-density,density])[0])

    # Repeat
    gates *= duplicates + 1

def make_rand_steps(
        n_steps: int = 8, 
        duplicates: int = 0, 
        even_density: float = 0.25, 
        odd_density: float = 0.25
    ) -> list[int]:
    
    gates = []

    for i in range(n_steps):
        if i%2 == 0:
            gates.append(random.choices([0,1],[1-even_density,even_density]))
        else:
            gates.append(random.choices([0,1],[1-odd_density,odd_density]))
    
    gates *= duplicates + 1

    return gates

def make_ksh(
        n_steps: int = 8,
        duplicates: int = 0,
        k_density: float = 0.25, 
        sn_odd_density: float = 0, 
        hh_density: float = 1, 
        hh_odd_density: float = 0
    ):
    """Make Kick, Hihat and Snare gates
    
    Ensure the following:
    1. There is a kick on beat 1
    2. There are snares on every 5th step, out of 8
    3. Kicks and snares never play at the same time

    Returns:
        kick_gates, snare_gates, hihat_gates
    """

    kick_gates = []
    snare_gates = []
    hihat_gates = []

    # Fill kick and snare steps
    for i in range(n_steps):
        if i == 0:
            # Always add kick on first step
            kick_gates.append(1)
            snare_gates.append(0)
        elif i%8 == 4:
            # Always add snare on 5th step of every 8
            kick_gates.append(0)
            snare_gates.append(1)
        else:
            # Decide on kick gate
            k = random.choices([0,1],[1-k_density,k_density])[0]
            kick_gates.append(k)
            if k == 0:
                # No kick, so maybe we put a snare on eh
                snare_gates.append(random.choices([0,1],[1-sn_odd_density,sn_odd_density])[0])
            else:
                snare_gates.append(0)

    # Fill hihat steps
    for i in range(n_steps):
        if i%2 == 0:
            hihat_gates.append(random.choices([0,1],[1-hh_density,hh_density])[0])
        else:
            hihat_gates.append(random.choices([0,1],[1-hh_odd_density,hh_odd_density])[0])

    kick_gates *= duplicates + 1
    snare_gates *= duplicates + 1
    hihat_gates *= duplicates + 1

    return kick_gates, snare_gates, hihat_gates
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

def rand_steps(
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

def gen_kick(n_steps: int = 8, duplicates: int = 0, density: float = 0.25) -> list[int]:
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

def gen_ksh(
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

def gen_hihats(n_steps: int, even_density: float = 1, odd_density: float = 0):
    """Generates step sequence typical for a hihat pattern.
    """
    hihat_gates = []
    for i in range(n_steps):
        if i % 2 == 0:
            hihat_gates.append(random.choices([1,0], [even_density, 1-even_density])[0])
        else:
            hihat_gates.append(random.choices([1,0], [odd_density, 1-odd_density])[0])
    return hihat_gates


def gen_kick_snare(n_steps: int, kick_density: float = 0.3, extra_snare_chance: float = 0.3):
    """Generates step sequences for kick and snare based on density.
    This algo is slightly different from gen_ksh, and will ensure proper density
    """
    n_snares = int(n_steps/8) # This will only work for 1/16 grids
    n_kicks = int(n_steps * kick_density)

    # We are going to insert set values for the first kick and the snares
    # So lets only add the required kicks
    kick_gates = [0] * (n_steps - n_snares - 1)

    snare_gates = [0] * (n_steps)

    for i in range(n_kicks):
        if i < len(kick_gates):
            kick_gates[i] = 1

    random.shuffle(kick_gates)

    kick_gates.insert(0, 1)
    open_steps = []

    for i in range(n_steps):
        if i % 8 == 4:
            kick_gates.insert(i,0)
            snare_gates[i] = 1

        # Add snares on steps without kicks
        else:
            if kick_gates[i] == 0:
                open_steps.append(i)
    
    n_extra_snares = int(extra_snare_chance * len(open_steps))
    random.shuffle(open_steps)

    for i in open_steps:
        if n_extra_snares > 0:
            snare_gates[i] = 1
            n_extra_snares -= 1
        else:
            break

    return kick_gates, snare_gates
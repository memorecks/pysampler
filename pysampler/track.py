from .step import Step
from .sample import Sample
import random
from copy import deepcopy

class Track:
    """Track class which contains steps (gates), groove and volume information"""

    def __init__(self, name: str = 'default') -> None:
        # TODO: Move Step 'delay' to Track 'delay' - not needed when we have swing and humanize
        self.steps: list[Step] = []
        self.name = name
        self.vol = 0
        self.monophonic = False
        self.pitch = 0
        self.effects = []
        self.samples: list[Sample] = [] # store Sample objects here
        self.midi_note = None

    def randomize_velocities(self, min: int = 0, max: int = 127):
        for step in self.steps:
            step.vel = random.randint(min, max)

    def humanize_steps(self, amount: float = 0, n_steps: int = 0, pos_delay: bool = False) -> None: 
        """
        Adds random amounts of delay to each step in a track in Ms.
        Replaces existing humanization.
        A number of steps to repeat random sequence can be defined in n_steps.
        If n_steps is 0 it will default to all steps.
        """
        # If no range specified, default to all
        if n_steps == 0:
            n_steps = len(self.steps)
        
        # Calculate delay range, make only positive if needed
        if pos_delay:
            random_shifts = [random.uniform(0,amount) for _ in range(n_steps)]
        else:
            #random_shifts = [random.uniform(0,amount)-amount/2 for _ in range(n_steps)]
            random_shifts = [random.uniform(-amount,amount)/2 for _ in range(n_steps)]

        # Set the humanize parameter for all steps
        for index, step in enumerate(self.steps):
            # Ensure positve delay on 1st step to avoid negative time index
            if index == 0:
                if random_shifts[index%len(random_shifts)] < 0:
                    step.humanize = 0
                else:
                    step.humanize = random_shifts[index%len(random_shifts)]
            else:
                step.humanize = random_shifts[index%len(random_shifts)]

    def duplicate_time(self, n: int = 1):
        for _ in range(n):
            self.steps.extend(deepcopy(self.steps))
        

    def set_delay(self, delay: float = 0.0):
        """Shifts steps by a factor of 1 step"""
        for step in self.steps:
            step.delay = delay

    def set_swing(
            self, 
            percentage: float = 0.0,
            distance: int = 1,
            vel_factor: float = 1.0,
            additive: bool = False,
            linn_scale = False
        ) -> None:
        """Set swing for all steps in Track with optional velocity scaling

        Args:
            percentage (float): Swing percentage 0..100
            distance (int): Number of steps between swing adjustment (1 is 1/16, 2 is 1/8)
            vel_factor (float): Scale swung step velocity as factor (0.0..1.0)
            additive (bool): Whether to add to existing swing level or not
            linn_scale (bool): Changes swing scale to 50..75
        """
        percentage = percentage/100

        # Convert swing scale
        if linn_scale:
            percentage = (percentage - 0.5) * 2
        else:
            percentage = percentage / 2

        mod = int(distance*2)
        for index, step in enumerate(self.steps):
            if index % mod == int(distance):
                if additive:
                    step.swing += percentage
                else:
                    step.swing = percentage
                step.vel = int(step.vel * vel_factor)

    def add_step(self, gate: int = 1, delay: float = 0.0, swing: float = 0.0, humanize: float = 0.0, vel: int = 127):
        """Add single step to track"""
        gate = bool(gate)
        self.steps.append(Step(gate=gate,delay=delay,swing=swing,humanize=humanize,vel=vel))

    def add_steps(
            self, 
            delay: float = 0.0, 
            swing: float = 0.0, 
            humanize: float = 0.0, 
            gates = [], 
            pitches = [], 
            velocities = []
        ):
        """Add steps to track

        Args:
            delay (float): shift all steps by a percentage of 1 step
            swing (float): shift every other step
            humanize (float): add random delays to steps
            vol (float): decibel level of steps
            gates (list[bool]): steps to add
        """
        # If no pitches or velocities specified, set defaults
        if len(pitches) == 0:
            pitches = [0] * len(gates)

        if len(velocities) == 0:
            velocities = [127] * len(gates)

        # If specified, make sure they are the same length as gates    
        if len(gates) != len(pitches):
            raise ValueError("Gates and pitches must be the same length")
        
        if len(gates) != len(velocities):
            raise ValueError("Gates and volumes must be the same length")

        # Add steps
        for i,gate in enumerate(gates):
            # Convert 0/1 to True/False if needed
            gate = bool(gate)
            self.steps.append(
                Step(
                    gate=gate,
                    delay=delay,
                    swing=swing,
                    humanize=humanize,
                    vel=velocities[i],
                    pitch=pitches[i]
                ))
    
    def add_effect(self, effect):
        self.effects.append(effect)
    
    def add_sample(self, path: str = '', pitch: int = 0, vol: float = 0):
        sample = Sample(path,pitch,vol)
        self.samples.append(sample)
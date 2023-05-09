class Step:
    def __init__(
                self, 
                gate: bool = False, 
                delay: float = 0.0, 
                swing: float = 0.0, 
                humanize: float = 0.0, 
                vol: float = 0.0, 
                pitch = 0, 
                vel: int = 127
            ) -> None:
        self.gate = gate
        self.delay = delay
        self.swing = swing
        self.humanize = humanize
        self.vel = vel
        self.vol = vol
        self.pitch = pitch
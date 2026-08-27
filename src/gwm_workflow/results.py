from dataclasses import dataclass, field


@dataclass
class SimulationResult:
    metrics: dict
    attrs: dict = field(default_factory=dict)

    def to_dict(self):
        return {"metrics": self.metrics, "attrs": self.attrs}

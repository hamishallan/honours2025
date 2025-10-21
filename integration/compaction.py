class CompactionCalculator:
    def __init__(self, loadcell):
        self.loadcell = loadcell  # expects .A and .g attributes

    def compute(self, weight_kg):
        """Compute soil compaction pressure in Pascals."""
        if weight_kg <= 0:
            return 0.0
        force_n = weight_kg * self.loadcell.g
        return force_n / self.loadcell.A

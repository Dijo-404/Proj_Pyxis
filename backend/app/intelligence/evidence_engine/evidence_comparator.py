from app.schemas.evidence import EvidenceComparison


def rank_comparisons(comparisons: list[EvidenceComparison]) -> list[EvidenceComparison]:
    return sorted(comparisons, key=lambda comparison: comparison.match_score, reverse=True)


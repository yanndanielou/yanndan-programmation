import os


def load_score(scorefile: str) -> int:
    """Returns the highest score, or 0 if no one has scored yet"""
    try:
        with open(scorefile) as file:
            scores = sorted([int(score.strip()) for score in file.readlines() if score.strip().isdigit()], reverse=True)
    except IOError:
        scores = []

    return scores[0] if scores else 0


def write_score(score: int, scorefile: str) -> None:
    """
    Writes score to file.
    """
    assert str(score).isdigit()
    with open(scorefile, "a") as file:
        file.write("{}\n".format(score))

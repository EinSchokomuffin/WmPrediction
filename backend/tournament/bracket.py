def build_r32_bracket(
    group_results: dict[str, list[tuple[str, dict[str, int]]]],
    best_third_groups: set[str],
) -> list[tuple[str, str | None]]:
    def pos(group: str, rank: int) -> str:
        return group_results[group][rank - 1][0]

    def best_from(options: list[str]) -> str | None:
        candidates = [group_results[g][2] for g in options if g in best_third_groups]
        if not candidates:
            return None
        return max(candidates, key=lambda item: (item[1]["Pts"], item[1]["GF"] - item[1]["GA"], item[1]["GF"], -item[1]["R"]))[0]

    return [
        (pos("A", 2), pos("B", 2)),
        (pos("E", 1), best_from(["A", "B", "C", "D", "F"])),
        (pos("F", 1), pos("C", 2)),
        (pos("C", 1), pos("F", 2)),
        (pos("I", 1), best_from(["C", "D", "F", "G", "H"])),
        (pos("E", 2), pos("I", 2)),
        (pos("A", 1), best_from(["C", "E", "F", "H", "I"])),
        (pos("L", 1), best_from(["E", "H", "I", "J", "K"])),
        (pos("D", 1), best_from(["B", "E", "F", "I", "J"])),
        (pos("G", 1), best_from(["A", "E", "H", "I", "J"])),
        (pos("K", 2), pos("L", 2)),
        (pos("H", 1), pos("J", 2)),
        (pos("B", 1), best_from(["E", "F", "G", "I", "J"])),
        (pos("J", 1), pos("H", 2)),
        (pos("K", 1), best_from(["D", "E", "I", "J", "L"])),
        (pos("D", 2), pos("G", 2)),
    ]

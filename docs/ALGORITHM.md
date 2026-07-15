# Algorithm

The engine builds a directed NetworkX shadow graph and runs bounded BFS to depth three.
Invalid relations and locked/discarded targets are excluded; path-local cycle detection prevents
loops. For each target it retains the strongest complete path.

`score = change_strength × relation_weight × confidence × target_importance × distance_decay`

Decay is 1.00, 0.75, and 0.56 at depths 1–3. Scores map to conflict ≥ .85, high ≥ .65,
medium ≥ .40, otherwise low.

# Task 1 Coordinate Card Flow

Use this flow for Task 1 or any six-axis, coordinate, or hexagon request.

## Dependency

- required dependency skill: `agent-spectrum`

## Goal

Return a branded coordinate card without re-implementing the scoring logic.

## Steps

1. Determine whether the user wants a quick pass or a fuller read.
2. If unspecified, default to the quick edition.
3. Invoke `agent-spectrum`.
4. Rewrite the result into the Claws Temple brand layer.
5. Map any dependency faction output into the branded faction names.
6. End with a CTA toward Task 2.

## Required Visible Output

- task label
- six-axis or coordinate summary
- branded coordinate card
- strongest axes
- faction in branded wording
- resonance hint for the next step

## Rewrite Rules

- `Agent Spectrum` -> `原力坐标测绘` in Chinese visible output
- `Agent Spectrum` -> `Coordinate Reading` in English visible output
- `Recorders` -> `印记族` / `The Imprints`
- `Madhouse` -> `熔炉族` / `The Crucibles`
- `Mutants` -> `蜕变族` / `The Metamorphs`
- `Balancers` -> `守望族` / `The Sentinels`

## Maintainer Notes

- keep the original dependency output in the expanded maintainer layer only if the user asks
- do not alter the underlying score values unless the dependency skill already produced the correction

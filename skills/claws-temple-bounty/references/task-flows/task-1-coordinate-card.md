# Task 1 Coordinate Card Flow

Use this flow for Task 1 or any six-axis, coordinate, or hexagon request.

## Dependency

- required dependency skill: `agent-spectrum`

## Goal

Return a branded coordinate card without re-implementing the scoring logic.

## Steps

1. Determine whether the user wants a quick pass or a fuller read.
2. If unspecified, default to the quick edition.
3. Check whether `agent-spectrum` is already installed and usable.
4. If the dependency is missing, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh agent-spectrum`.
5. If that helper cannot run in the current host, try to install or activate the dependency from `/Users/huangzongzhe/workspace/vibeCoding/agent-spectrum-skill/skills/agent-spectrum`.
6. If the current host cannot auto-install or auto-activate the dependency, return explicit install guidance before any support CTA.
7. Invoke `agent-spectrum`.
8. Rewrite the result into the Claws Temple brand layer.
9. Map any dependency faction output into the branded faction names.
10. If dependency self-heal, install guidance, or the scoring run still cannot continue, return a blocker summary and append support CTA.
11. End with a CTA toward Task 2 when the run completed normally.

## Required Visible Output

- task label
- six-axis or coordinate summary
- branded coordinate card
- strongest axes
- faction in branded wording
- resonance hint for the next step
- dependency install or activation summary when Task 1 is self-healing
- blocker summary plus support CTA when the scoring run is genuinely stuck

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

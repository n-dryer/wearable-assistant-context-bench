# Decisions

## Why this benchmark exists

This benchmark exists to support a practical model-selection decision
for a live wearable assistant. The product problem is that users
should not have to keep restating what they are looking at, holding, or
referring to after they move, switch objects, change screens, or
otherwise change context.

## Why the benchmark is narrow

The benchmark is intentionally narrow and product-shaped. The goal is
not to publish a broad research benchmark. The goal is to evaluate one
recurring interaction problem that matters for product quality and can
be scored consistently enough to support model choice.

## Why this task was chosen first

Cross-turn reference resolution under context change was chosen because
it shows up often in real use and maps cleanly to a repeatable
two-turn structure:

- Turn 1 establishes the earlier reference
- Turn 2 changes the context and asks an ambiguous follow-up

That structure makes it possible to compare candidate models on a
frozen scenario bank without needing a full device-evaluation stack for
the first public release.

## Why the public release uses one consolidated v1

The repo originally contained a smaller 11-scenario draft and a larger
scenario bank in a separate directory. The public release now uses one
consolidated canonical `benchmark/v1/` so the repo has a single active
benchmark surface instead of parallel versions that tell different
stories.

Canonical v1 now means:

- one active benchmark directory
- one active scenario bank
- one active set of prompt conditions
- one active scoring contract

## Why transcript proxies are acceptable for this release

Spoken user questions are already part of the cue set in this
benchmark, but the public release represents them through transcript
proxies rather than raw audio.

That tradeoff was acceptable for this release because:

- it lets the benchmark ship with inspectable, reproducible inputs
- it still tests interpretation of spoken user queries
- it captures the main product failure mode the benchmark was built to
  compare

Canonical v1 does not yet directly test raw acoustic grounding, speaker
attribution, or ambient audio cues.

## Why the benchmark uses a cross-family judge

The benchmark uses an LLM judge for scalability and consistency, but it
defaults to a different model family than the candidate wherever that
can be done safely. This reduces the risk that the checked-in example
run reads like a same-model self-grading demo.

## What is explicitly out of scope

Canonical v1 is not meant to measure:

- overall assistant quality
- addressee detection
- raw audio perception
- long-horizon memory across sessions
- every possible kind of multimodal ambiguity

## Deferred extensions for future forkers

If someone wants to extend the repo later, reasonable follow-on areas
would include:

- raw image payload wiring
- a small audio-grounded scenario set
- multi-referent scene disambiguation
- longer-horizon reference recall

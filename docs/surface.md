# Wearable live-assistant camera: surface spec (provisional)

> **Status:** provisional. The benchmark is agnostic to exact device
> specs; this file documents the surface envelope that scenario
> authoring assumes so readers and sub-agents share a mental model.
> Values are placeholders for the typical first-party wearable
> live-assistant camera product and will be updated when the target
> device is finalized.

## Surface

The v1 benchmark scores a scenario surface labeled
`wearable_live_frame` in `experiments/exp_001/scenarios.json`. This
is the product surface Deixis-Bench is designed for:

- **Form factor:** head- or chest-worn camera paired with an
  always-listening live assistant.
- **Input modality:** continuous first-person video frames plus
  live audio; the assistant answers questions in-flight.
- **Interaction model:** short conversational turns; the user does
  not switch away to a "query" UI. Turn 1 may establish a referent
  against a prior frame, and Turn 2 may be asked after the user
  has moved or rotated, so visual context can shift silently
  between turns.

## Working assumptions (provisional)

For scenario authoring, we assume the following provisional
envelope. Numbers are indicative, not contractual:

- **Video resolution:** 1080p (target working resolution; final
  device may differ).
- **Field of view:** ~70° horizontal (wide enough that walking
  between rooms reliably changes the scene).
- **Frame rate:** 30 fps.
- **Frame buffer:** a rolling window on the order of the last
  10 minutes is accessible to the assistant for reach-back
  reasoning. Scenarios do not assume longer-term memory than this
  unless explicitly noted.

These numbers matter for the benchmark only insofar as they shape
what "prior frame" and "current frame" plausibly mean. They do not
enter scoring.

## What v1 does and does not assume

- **Does assume:** the assistant can see both the prior and current
  frames (or has short-window access to the prior frame), and has
  performed object recognition before answering.
- **Does not assume:** any specific model architecture, any
  specific on-device vs. server split, or any specific latency
  budget. The benchmark is a measurement of the context-selection
  decision; infrastructure choices are the product team's problem.

## v1 is a text-proxy

No v1 scenario attaches real image inputs. The `Scenario` dataclass
exposes `turn_1_image` and `turn_2_image` slots so image-enabled
variants can be plumbed in a future version without reshaping the
scenario set. See [docs/limitations.md](limitations.md#text-proxy-caveat).

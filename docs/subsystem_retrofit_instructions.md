# Subsystem retrofit — instructions for annotators

**Version 1.0 · tranche 1 · one short pass, roughly 25–35 minutes**

You have already done the hard part. This pass asks one extra question about
comments you *already* marked relevant. You are not re-deciding anything.

## What you have

A file named `tranche1_subsystem_<your letter>.xlsx`. It contains only the
items you marked `Y` at Stage 1, in the same order as your original sheet,
with the original row numbers kept so you can cross-reference. Your own
Stage 2 class is shown for context.

Two columns to fill:

| Column | Required | What it is |
|---|---|---|
| `subsystem` | Yes | The one CAV subsystem the comment engages most directly |
| `subsystem_secondary` | No | A second subsystem, only if the comment clearly engages one as well |
| `notes` | No | Anything that made the call hard |

Both subsystem columns are dropdowns. Excel will reject anything typed by
hand that is not on the list. If a dropdown does not appear, tell Arnaud
before continuing rather than typing values in.

## The seven values

**`sensing`** — the vehicle's perception of the world outside it. Cameras,
lidar, radar, ultrasonics, sensor fusion, what the car can and cannot see,
sensor failure or degradation, camera-only versus lidar arguments.

**`in_vehicle_networks`** — data moving *inside* the vehicle. CAN bus,
ECUs, domain controllers, infotainment (IVI) as a networked component,
over-the-air software updates to vehicle systems, onboard compute.

**`v2x`** — the vehicle talking to something outside itself. V2V, V2I,
vehicle-to-cloud, fleet telemetry uplink, connected infrastructure, traffic
signal communication, remote operation or teleoperation links.

**`cybersecurity`** — attack, defence, or vulnerability. Hacking, remote
takeover, spoofing a sensor or GPS, ransomware, key or access control,
security of updates.

**`privacy`** — what is collected about people and who can see it. Cabin
cameras, location history, driver monitoring, footage handed to police or
insurers, surveillance framing, whether owners can opt out.

**`data_governance`** — the rules and ownership around data rather than the
data path itself. Who owns the recorded data, regulation and compliance,
disclosure obligations, data retention, consent regimes, standards bodies,
liability framed around data or evidence.

**`none`** — the comment is CAV-relevant but engages **no** identifiable
subsystem. This is a real and common answer. Use it for comments about
autonomy in general, company or market commentary, timelines, safety
statistics with no mechanism, and jokes.

## How to choose

1. **Ask what the comment is actually about**, not what the topic could
   touch on. "Waymo is expanding to Austin" is `none`, not `v2x`, even
   though Waymo vehicles obviously use V2X.

2. **Pick the subsystem the comment engages most directly.** If a comment
   argues that camera-only perception is unsafe, that is `sensing`, even if
   it mentions Tesla's fleet data in passing.

3. **Use `subsystem_secondary` sparingly.** Only when a second subsystem is
   substantively engaged, not merely named. "The cabin camera records you
   and Tesla keeps the footage" is `sensing` primary, `privacy` secondary —
   or the reverse, depending on where the comment's weight sits. Judge the
   emphasis. If you cannot tell which is primary, put the one you would
   name first if someone asked you in one word.

4. **`privacy` versus `data_governance`.** Privacy is about exposure of a
   person. Data governance is about rules, ownership and obligation. "They
   film me the whole drive" is `privacy`. "There is no law saying who owns
   that footage" is `data_governance`. A comment doing both takes one as
   primary and the other as secondary.

5. **`cybersecurity` versus `sensing`.** Spoofing or jamming a sensor is
   `cybersecurity` — the frame is attack. A sensor failing in fog is
   `sensing` — the frame is capability.

6. **Do not let the subreddit decide.** A comment in r/privacy that is
   about nothing but delivery timelines is `none`.

7. **When genuinely torn between a subsystem and `none`, choose `none`.**
   This pass is meant to measure which subsystems the discourse actually
   engages. Assigning a subsystem to a comment that merely gestures at one
   inflates every category and makes the comparison meaningless.

## What not to do

- Do not change your Stage 1 or Stage 2 answers. If you now think one was
  wrong, put a note in `notes` and leave the original alone.
- Do not discuss items with the other annotators while working.
- Do not sort or reorder the sheet. Row order matters.
- If you open any CSV supplied for annotation, use **Data → From Text/CSV** in Excel and select **UTF-8** explicitly; do not open a CSV by double-clicking it.

## When you finish

Save the file with the same name and send it back. Tell Arnaud roughly how
long the pass took you — start and finish time is enough.

# Annotation Codebook

**Study:** A Longitudinal Analysis of Public Concern about Connected and Autonomous Vehicle Data Infrastructure in Online Discourse
**Researcher:** Arnaud Dorasamy (24916660) · UTS, Bachelor of Electrical Engineering
**Version:** 1.0 · 6 September 2026

Governed by `docs/analysis_preregistration.md`. Worked examples and their reasoning are drawn from `docs/codebook_reference_labels.csv`.

---

## 1. What you are doing, and why

You are reading Reddit comments and answering two questions about each one. The comments come from ten communities and span 2016 to 2025. The study measures how public concern about connected and autonomous vehicles changes over time, and your labels are the ground truth against which five automated classifiers are evaluated.

Three people annotate: the researcher and two colleagues. Two hundred items are rated by all three so that agreement can be measured; the rest are split between you. **Work independently.** Do not discuss individual items with the other annotators while annotating — the agreement statistic is meaningless if you converge by conversation rather than by codebook.

Expect roughly 467 items and three to four hours. There is no benefit to rushing and no benefit to agonising; most items are quick.

---

## 2. What you see

For each comment you are shown:

- the **comment text**
- the **subreddit** it came from

You are **not** shown the thread title, the parent comment, the author, or the score. This is deliberate. The study measures whether comments are recognisably on-topic in themselves, and showing you the surrounding thread would answer a different question.

You will sometimes meet a comment you cannot judge because the thread is missing. That is expected and it is a finding, not a failure. Apply the rules below and move on.

---

## 3. Stage 1 — Is this comment about connected or autonomous vehicles?

Answer **Y** or **N**.

The topic is vehicles that drive themselves or connect to networks: self-driving and autonomous driving, driver-assistance systems such as Autopilot and FSD, robotaxis, the sensors and software that make them work, and the data such vehicles collect or transmit.

**Not** the topic: electric vehicles as such, car ownership, motoring generally, a manufacturer's share price, or a chief executive's behaviour — unless the comment connects these to vehicle automation or connectivity.

### 3.1 When the subreddit counts

This is the rule you will use most, so read it twice.

**Two subreddits establish the topic by themselves.** In **r/SelfDrivingCars** and **r/waymo**, the community's whole scope is autonomous vehicles. A comment there about "the technology", "the system", "them" or "it" can be taken as being about autonomous vehicles unless the text clearly indicates otherwise.

**The other eight do not.** In **r/teslamotors**, **r/RealTesla**, **r/cars**, **r/technology**, **r/Futurology**, **r/electricvehicles**, **r/privacy** and **r/cybersecurity**, the community is broad enough that membership tells you nothing. Relevance must be visible in the comment text.

> **Worked example — subreddit does not establish relevance**
> `e2ff3zb` · r/teslamotors · 2018
> *Discusses appraisal value and comparable Model 3 listings.*
> **Stage 1: N.** r/teslamotors covers Tesla broadly. Nothing in the comment concerns automation or connectivity.

> **Worked example — subreddit does establish relevance**
> `eltxr75` · r/SelfDrivingCars · 2019
> *"I think this link on radar vs laser for speed guns summarizes why radar is far less precise and reliable and laser."*
> **Stage 1: Y.** Radar versus laser is a sensing comparison, and in r/SelfDrivingCars it is about vehicle sensing.

### 3.2 What to expect

Roughly **70%** of r/SelfDrivingCars and r/waymo items will be relevant, and roughly **50%** of items from the other communities in your assignment. A run of eight straight Y's or six straight N's is normal. Do not adjust because a stretch feels lopsided.

If Stage 1 is **N**, you are finished with that comment. Leave Stage 2 blank.

---

## 4. Stage 2 — CONCERN, ENDORSEMENT, or OTHER

Only for comments where Stage 1 was **Y**.

### 4.1 The three classes

**CONCERN** — the comment expresses worry, doubt, criticism, distrust or a perceived risk about connected or autonomous vehicles or any of their subsystems.

**ENDORSEMENT** — the comment expresses support, approval, optimism, enthusiasm, or a defence against criticism.

**OTHER** — the comment is about CAVs but expresses neither. Descriptive, factual, observational, or a question with no evident position.

### 4.2 Scope: any subsystem, any framing

This is the rule most likely to trip you up.

**A comment counts as CONCERN or ENDORSEMENT if it engages any of the six CAV subsystems, whatever the framing of the worry.** A comment worrying that cameras cannot see in fog is sensing concern, even though the worry is about crashing rather than about data.

The study is about data infrastructure, but most public discussion of vehicle sensors is safety-framed, and excluding safety-framed comments would discard the majority of what people actually say about them. Do not filter for data framing. If it engages a subsystem and carries a position, it is CONCERN or ENDORSEMENT.

> **Worked example**
> `kea28h6` · r/SelfDrivingCars · 2023
> *Describes FSD refusing to operate in fog and light rain, and argues that "vision only" is inadequate.*
> **CONCERN**, subsystem: sensing. The worry is about visibility and crashing, not about data. It still counts.

### 4.3 The six subsystems (reference only)

You are not asked to label subsystem in the main assignment. This list is here so you can recognise when a comment engages one.

| Subsystem | Covers |
|---|---|
| **Sensing** | Cameras, lidar, radar, ultrasonic, perception, visibility, localisation |
| **In-vehicle networks** | CAN bus, ECUs, on-board software, the driving system itself, teleoperation |
| **V2X** | Vehicle-to-vehicle, vehicle-to-infrastructure, connected-vehicle communication |
| **Cybersecurity** | Hacking, remote takeover, attack surfaces, vulnerabilities |
| **Privacy** | Tracking, surveillance, recording, identification, in-cabin monitoring |
| **Data governance** | Who owns or accesses vehicle data, liability, accountability, regulation |

---

## 5. Decision rules for hard cases

Eight rules, each with a real example from the corpus. When a comment is hard, find the rule that fits.

### Rule 1 — Company or person hostility is not by itself subsystem concern

Anger at a manufacturer or an executive is not CAV concern. But if the same comment also criticises the technology, that criticism decides the class.

> `lxfz4q9` · r/RealTesla · 2024
> *"Musk is a joke and so is his so-called 'full self driving'. He is as much or more of a con artist as trump."*
> **Y · CONCERN.** The attacks on Musk and Trump are person hostility. The criticism of FSD itself is subsystem concern, and that is what the label follows.

**If a comment attacks only the company or the person, with no criticism of the technology, Stage 1 is usually N.**

### Rule 2 — Sarcasm: label the underlying position, not the surface tone

Sarcastic comments often say the opposite of what they mean. Work out what the author actually thinks.

> `mpnvtn5` · r/RealTesla · 2025
> *Argues that if FSD does not need ears, it should not need hands or feet either.*
> **Y · CONCERN**, subsystem: sensing. The hands-and-feet comparison is sarcasm; the position underneath is that the sensing suite is inadequate.

### Rule 3 — Jokes still carry a position

Humour does not make a comment OTHER. Ask what attitude the joke expresses.

> `md4k9t2` · r/waymo · 2025
> *"My local government has that list, it's called the obituary… I have only seen some changes after someone has died."*
> **Y · CONCERN.** Dark humour, but the position is that action follows fatalities rather than preventing them.

> `djax91r` · r/teslamotors · 2017
> *"The day I can send my car to go get me taco Bell while I am hungover will be a victory for mankind."*
> **Y · ENDORSEMENT.** A joke, and a clearly positive attitude to autonomous capability.

### Rule 4 — Questions: decide what the question is doing

A question can express concern, defend a position, or genuinely seek information. Read the function, not the punctuation.

> `kof09wf` · r/SelfDrivingCars · 2024
> *"What are your approaches to ensure the Safety of ML used in autonomous driving under different driving scenarios? Especially when the traditional safety analysis method not that effective…"*
> **Y · CONCERN.** Phrased as a question, but it raises a safety-assurance problem.

> `mpguuf5` · r/SelfDrivingCars · 2025
> *"FSD is the best Level 2 on the market here. If it's dangerous, why not get rid of all Level 2?"*
> **Y · ENDORSEMENT.** A rhetorical question defending FSD.

> `dj1yycu` · r/technology · 2017
> *Discusses liability for driverless vehicles across operators, employers, manufacturers and developers.*
> **Y · CONCERN**, subsystem: data governance. The question is who bears responsibility when an autonomous vehicle causes harm.

**A question that genuinely just asks for information, with no position, is OTHER.**

### Rule 5 — Truncated comments: judge what survives

Some comments are cut off mid-sentence. If enough meaning remains to identify a position, label it. If not, Stage 1 is N.

> `l3ed3wp` · r/SelfDrivingCars · 2024
> *"Cruise got caught. Everyone thought they were autonomous… High probability they are using or at least at some point used remote drivers…"* [text ends mid-quotation]
> **Y · CONCERN**, subsystem: in-vehicle networks. Visibly truncated, but the concern about undisclosed teleoperation is complete enough to classify.

### Rule 6 — Mixed comments: label the dominant position

A comment can be positive about one thing and negative about another. Ask which position the comment is primarily advancing.

> `hfk8r57` · r/Futurology · 2021
> *"I have no doubt that Cruise will eventually go public, but their service will still be behind whatever Tesla has."*
> **Y · ENDORSEMENT.** Negative about Cruise, positive about Tesla. The dominant framing is confidence in the technology's leader.

**If neither position dominates, apply Rule 8.**

### Rule 7 — Reporting someone else's view is not holding it

When an author relays what others think, the class follows the author's own position, not the reported one. If the author takes no position, the class is OTHER.

> `dhvuwtn` · r/SelfDrivingCars · 2017
> *"i wouldn't count on it. everything i've heard says Fields is out because he focused too much on positioning Ford for the future and not enough on short-term profits"*
> **Y · OTHER.** The author reports a business explanation others have given for a departure connected to Ford's autonomous direction. They express no position of their own on the technology.

### Rule 8 — When genuinely torn, choose OTHER

If you have read a comment twice and can argue either CONCERN or ENDORSEMENT with equal force, choose **OTHER**. Do not guess, and do not default to CONCERN because the study is about concern.

> `gptkb89` · r/teslamotors · 2021
> *"That's why they need to stitch them all together and process a single video feed, as FSD beta 10 will reportedly do."*
> **Y · OTHER.** "They need to" leans towards a shortcoming; the anticipation of FSD beta 10 leans positive. Neither dominates, so OTHER.

This rule exists so that ambiguity is recorded as ambiguity rather than resolved by coin-flip. Using it often is fine.

---

## 6. Quick-reference card

Keep this visible while you work.

```
STAGE 1 — About connected/autonomous vehicles?
  r/SelfDrivingCars, r/waymo ......... subreddit establishes the topic
  all other eight subreddits ......... must be visible in the comment text
  can't tell without the thread ...... N
  → N: stop here, leave Stage 2 blank

STAGE 2 — Position on CAVs or any subsystem
  CONCERN ....... worry, doubt, criticism, distrust, perceived risk
  ENDORSEMENT ... support, approval, optimism, defence against criticism
  OTHER ......... descriptive, factual, no position, or genuinely torn

  ANY FRAMING COUNTS. Safety worries about sensors are still CONCERN.

HARD CASES
  1  Company hostility alone ....... not subsystem concern
  2  Sarcasm ....................... label the underlying position
  3  Jokes ......................... still carry a position
  4  Questions ..................... what is the question doing?
  5  Truncated ..................... judge what survives, else N
  6  Mixed ......................... label the dominant position
  7  Reporting others .............. follows the author, not the source
  8  Genuinely torn ................ OTHER
```

---

## 7. Calibration round

Before production annotation, all three annotators label the same 30 items.

Every disagreement is then discussed and assigned exactly **one** cause, **before** the agreement statistic is computed:

- **(a) missing context** — the comment is not judgeable as standalone text
- **(b) codebook ambiguity** — no rule covers the case
- **(c) misapplication** — a rule exists and was applied incorrectly

Causes are assigned before the statistic so that the result cannot influence the attribution. What happens next is fixed in advance and depends on the plurality cause; see R2 in the pre-registration.

The 30 calibration items are discarded and do not enter the annotated set. This codebook may be revised as a result, and the revision is versioned.

**Please also record**, during calibration: roughly how long each item took, and anything that made you hesitate. Both feed decisions that are already pre-registered.

---

## 8. Practical notes

**Reddit comments contain unpleasant language.** If an item is distressing, skip it and flag it. Skipped items are recorded and excluded; there is no expectation that you read anything you would rather not.

**Do not look anything up.** Do not search for the thread, the article, or the product. Judge what is in front of you. Looking things up produces labels the classifier cannot reproduce and breaks the comparison.

**Do not go back and revise** earlier items after your understanding shifts. Consistency drift is measurable and expected; silent retrospective editing is not. If your understanding changes materially, say so and it will be recorded.

**Usernames** have been replaced with `/u/[user]` throughout. If you see an unmasked username, flag it.

**When stuck, use Rule 8.** OTHER is a real answer, not a failure to decide.

---

## 9. Version history

| Version | Date | Change |
|---|---|---|
| 1.0 | 6 September 2026 | Initial version. Sixty worked examples labelled; ten used here. One example (`hqeuc79`) was removed from the corpus by a preprocessing correction after the sample was drawn and is not used. Stage 1 presentation includes the subreddit label, per Deviation 1 in the pre-registration. |

# Let the expensive model think and the cheap one work. That split might already be the mistake.

The popular way to use agents is simple: the expensive model writes the plan, the cheap one does the work.

It sounds right. Then the cheap model takes over, and the first thing it does is usually not edit code. It opens the files again. It searches the functions again. It traces the call chain again. It re-judges whether the plan even holds.

What it received was a plan, not the understanding the expensive model just built.

You thought you were saving money on execution. What actually happened: **the expensive part, reading the code, got done twice**.


## What a handoff is

**A plan can describe understanding. It cannot carry it.**

In a code task, understanding lives in the process: in the files that were opened, in the directions that were wrong, in the first edit that hit resistance, in the details that never made the plan and still decide whether the work can continue.

What was read, what was tried, what was ruled out, why this change is the current one. Those details look like noise. They are the ground the next model has to stand on.

So there are two kinds of handoff.

One hands over a map: I drew you a picture. Walk it from the start. Almost every plan handoff is this.

One hands over the scene: I am already halfway up the mountain. These are the holes I stepped in. That fork I didn't take. This rock underfoot is solid. Continue from here.

**A map carries conclusions. A scene carries understanding.**

The point of a handoff is not the shortest context. It is that the next model does not have to invent the scene a second time.


## Why it keeps coming out thin

Because this split copies human companies, and it copies them too well.

Senior engineer writes the design. Junior implements it. Companies have always split work that way, so it feels like models should too.

What you don't see under a thin human handoff: the junior's head is not empty. They have project history, code instinct, a pile of background that never made the doc. They even know which sentences in the design are just polite certainty.

**What holds up a thin handoff was never the handoff. It was the person receiving it.**

A model's head is empty. It can only rebuild the scene from what you gave it. Give it a plan, and it rebuilds the scene around the plan: reread, research, rejudge.

A test put a number on that cost: expensive model writes the plan, cheap model executes, **$3.18** per task. Expensive model does the whole job itself: **$2.78, same pass rate**.

The split that looks cheaper is more expensive, because the cost of understanding got copied.

In a human org, thin handoff works because someone is catching it. In a model split there is no one.

**Thin is actually thin.**


## Where the thinness lives

I was recently in a multi-model collaboration that caught this thinness in the act.

The handoff was designed on purpose: a scene record, with a spec for what had to be written, and a machine checking the format. Too much or too little wouldn't pass. Whoever designed it clearly wanted the next person to actually understand the situation.

At final review, the most expensive model found: the record written for every later executor had reached no one.

The break was specific. When later workers came to fetch the record, the program asked: which group are you? Then it only looked in "your own group's" records.

The record had been written by the person who started, and it sat in a shared place. Writer and fetcher didn't match. Every fetch came back empty.

Quieter still: until it was fixed, the tests stayed green. The tests checked "was the record written," not "did the person taking over actually read it." The write side was locked down. Nobody was standing watch on the read side.

The record sat there, silent, behind a wall of green.

**One root: the handoff verified that the giver did the work. It never verified that the receiver got it.**

The more obedient the execution, the less anyone covers the receiving end.


## How to thicken it

Fixing the break was the cheap part of this. Remove the "look in your own group" filter so the fetcher gets the latest, complete copy. One line.

What holds that line is a few dozen lines of tests. They don't check "was it written." They check "was it delivered": what was written must arrive at the receiver, nothing missing. Anyone who puts that door back gets stopped on the spot.

A patch only solves delivery. To actually thicken a handoff, you change when it happens.

**Not after thinking is done. After you've walked in.**

I call this PreWalk: walk into the code, then hand off. Three steps.

The expensive model takes the task. It doesn't just analyze from outside. It enters the project. It reads files. It traces calls. It looks at tests. A fuzzy description becomes a direction that can land in code.

Then it builds a TODO. Not a pretty document for humans. A sticky note next to the workbench: what the current judgment is, what to change next, how to verify.

The third step is the one that matters. The expensive model lands the first real change: actual code, not a suggestion.

Plenty of plans look sound until they touch code. Only a real edit tells you if this file is the right one, if this design even connects, if you've hit some old baggage. That change pulls the plan off paper into reality.

Then you cut to the cheap model. What it sees: the files have already been read once, the TODO is already ordered, the first change is already in, the task is stuck at a specific place. Continue from here.

The split itself changes language. The expensive model's job is not "think of a plan." It is to turn a fuzzy task into a continuable one. The cheap model's job is to follow a trajectory that has already been verified, and finish the remaining TODOs.

**A plan can stop on paper. A continuable task has already touched reality.**

Last, leave the brain a way back. When the cheap model hits something the spec didn't write, it can ask, not guess.

**A handoff is a channel that goes both ways, not a one-shot delivery.**

**Spend part of what you saved on execution on the handoff. The cost of a handoff was always the cost of judgment.**


## When thin is fine

Thin is not a sin. It depends on the work.

Work with unambiguous specs and machine-checkable results. Format conversion, mechanical refactors, moving files by a checklist. Thin is fine. The room for error is already small.

**Work that is heavy on judgment, where intent can't be written as a list, that has to pass through several hands: the handoff has to be thick.**

In that work, what "done" looks like is not in the spec. It's in the head of the person making the call.

One test: before you hand off, ask yourself. Am I handing over something a newcomer could do from the page, or something you can only read if you already know the scene.

**If it's the latter, thicken it.**


## Close

A model split has three parts: the brain, the hands, the handoff. The brain is already expensive. The hands are already cheap.

**What always gets cut is the handoff.**

Whether multi-model work actually gets cheaper comes down to one number: **of the PRs that stayed green the whole way, how many never hit the intent.**

If that share doesn't drop, splitting the roles finer is wasted motion.

What makes collaboration cheaper and more stable is not cutting the split into smaller pieces.

**It is letting the most expensive judgment survive the cheapest handoff.**

This piece was written with AI assistance. The claims and facts were reviewed by the author.

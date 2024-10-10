<!-- title: Diffusion Reaction Game -->

I went to a [workshop](https://www.cs.rochester.edu/u/shossei2/eagl2024website/index.html)
last weekend, where I had the pleasure of hearing Avi Widgderson speak.
Avi recently won the Turing Award and is the only human ever to have won both the Turing Award
(in computer science) and the Abel Prize (in mathematics).
For his Turing Award lecture, Avi read through all of Alan Turing's papers,
and honored Turing by presenting his impressions, 
along with some lesser-known results and quotations.

Anyway, one of the papers Avi showed was Turing's [morphogenesis paper](https://royalsocietypublishing.org/doi/10.1098/rstb.1952.0012).
In the paper, Turing lays out a toy model for how developing biological organisms,
starting from a blob of undifferentiated cells, form spatially structured tissues.
His model involves a single chemical diffusing throughout the cells and taking place in local reactions.

Jumping forward to today: at breakfast my girlfriend and I were discussing
this year's Nobel prize awarded to the discoverers of micro-RNA.
(I'm not obsessed with prestigious awards, but they
do serve as Schelling points for fun discussions!)
Micro-RNA are short RNA sequences, roughly 20 nucleotides,
that as I understand help to regulate gene expression
by bonding to mRNA on their way to becoming proteins.
Honestly, that these exist is kind of obvious in hindsight!
mRNA on its way to becoming a protein is single stranded,
which permits sequence-dependent binding of other RNA.
What a perfect programming tool for Nature!

This got me thinking about what *is* Nature's programming model,
and of course Turing's reaction-diffusion setup sprung to mind.
It seems to me that the *idea* of micro-RNA could be captured
in a simple reaction-diffusion model with multiple diffusing chemicals.
What would programming in such a model be like? 

Imagine a puzzle game with some target state.
Maybe the goal is to produce a certain molecule Z.
Molecules X and Y are bouncing around, and
once they bump into each other, they will combine
to form Z.
But at the start of the level, 
there is a lot of A, which degrades X.
To win the level, one has to figure out how to get
rid of the A. Maybe one solution is to change the sequence
of the micro-RNA being produced, so that it bonds
to the messenger RNAs for A and prevents them from
being translated. It would take some parameter tuning
and design work to make a fun version of this game,
but it could capture a lot of fun biology.
You could play as a virus trying to hack a cell's defenses,
as the cells get more and more complex.
The connections to computer science could also be fun---
you could build a conditional statement, or a counter.

I'll end this note with some fun speculation;
would this kind of a programming model be of any use
in computer science? Probably not---what a nightmare,
to implement even a simple conditional or loop
in simulated chemistry! However, Nature's programming model
(in real life, not as captured by the idealized reaction-diffusion model)
has some advantages. Computer programs running in silicon
typically rely on extremely low failure rates and 
can be very brittle. In contrast, Nature has figured out
how I can run continuously for 28 years and counting
without any fatal crashes. And what about security?
In computer security, once a virus starts executing,
it has essentially won. But in biology,
a virus can replicate billions of times inside our bodies
and still lose.
Would a biologically-inspired programming model
suggest security measures paralleling immune systems in animals?
Biology had to think about robustness and security from the get-go,
in a highly adversarial context.
Maybe us computer scientists could learn a thing or two from
what Nature built.
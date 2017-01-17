# S4x17CTF
Challenge problems and solutions from the S4x17 CTF contest

This repo will only contain the challenges made by RevICS Security/Reid Wightman.

Each challenge contains various files including:
- notes: a general description of the challenge and how to administer it
- clue.txt: a challenge clue
- answer.txt: the actual flag value
- solve.txt: instructions for solving the flag (spoilers)

# Challenges
## PageMeMaybe

This challenge was a SDR problem.  Our Killer Robots were in the process of rolling out 2FA for their servers, but were using an ancient pager system to do it. Instead of relying on insecure POCSAG, they decided to roll their own encryption system on top: messages observed by players are hex-ascii. Obviously the robots are using some kind of decryption application to decode their pages.

Players can learn a bit about SDR decoding on this challenge, and can break a very simple encryption algorithm.  Players really seemed to enjoy this challenge during the CTF, much to the Judge's chagrin -- the Judge Pager was beeping constantly on Day 1 and Day 2 of the contest.


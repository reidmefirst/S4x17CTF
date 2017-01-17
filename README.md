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

This challenge couldn't have been done without help from Stephen Hilt, who tossed around ideas for adding encryption. You can find a research paper by him @ Trend Micro detailing the use of legacy pagers in SCADA/ICS/Medical systems.

## DNSTunnel

This challenge has players analyze a PCAP which contains a mysterious data exfiltration.

Opening up output.pcap we see a lot DNS queries of some peculiar names.

The hostname part of each query contains a chunk of data from a file that has been base58-encoded.  Rather than implement an actual client and server, we generate the PCAPs using the enclosed Python.  Using the scripts, we can encode any file that we want.

The vision for the protocol is that an A record request is made with a chunk of data. The server acknowledges receipt of the chunk by issuing a host record in return.

One of the chunks failed to reach our DNS server, so our client retransmitted it. This is meant to throw players off a little (and, is the reason that we wrote Python to generate the PCAP, we were lazy and didn't want to make a router drop a DNS packet or something stupid).

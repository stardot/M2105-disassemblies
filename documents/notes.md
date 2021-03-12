# Notes on v3.5 of the BT Merlin M2105 ROMs

## Configuration

The ROMs can be installed in banks 0-3 and 12-15. It helps to install IC22 in a
high bank so that it has higher priority than the BASIC ROM.

## Start up

IC22 is the M2105 Terminal 1 ROM, and this is the only ROM in the set with a
valid language entry. As a result, installing this in a high bank causes the
M2105 to boot into the language it provides.

Pages 30 to 3f are written:

 * The first byte of each page contains the page number.
...?
 * $aa55 is written to each pair of bytes in the page.
 * Zero is written to all bytes in the page.

Pages 4 to 7 are written:

 * The first byte of each page contains the page number.
 * $55aa is written to each pair of bytes in the page.
 * $aa55 is written to each pair of bytes in the page.
 * Zero is written to all bytes in the page.

Code at 822b in IC22 are copied into RAM at $3300.

## ROM banks

The bank containing each ROM is stored in an array at $515-$51d.

Each ROM has its own ID at $bf00. This is used as the index into the array.
Since the IDs are 1-4, addresses $516-$519 will contain the ROM banks for each
ROM. This is used to page in a specific ROM.

Each ROM also has arrays of entry points with high address bytes at $bf01 and
low bytes at $bf80. These are called via $3300 with X referring to the entry
in the array. The value of X is actually across *all* ROMs

The code to jump to routines via $3300 is copied from $822b when starting up.
The code to locate the ROMs and build the array at $516 is copied to $3366.
This code is overwritten later.

## Key presses

The terminal checks for the keys E, T, H and N on start up.

## ADFS check

IC24-SK2 contains code to check the current filing system. If it is ADFS, it
issues a *MOUNT command, closes all files, opens a file called M2105 for
reading and writing then tries to read it.

It uses $3d16 as the location of a parameter block for OSGBPB and reads 64
bytes of data into the memory at $3cd6, which means that the updated address in 
the block is $3d16, which is confusing to see.

## Paging JIM (page FD)

The 256 bytes paged in at $fd00 are controlled by the paging register at $fcff.
Assuming 32K RAM, paged from 0 to $7f, it's strange to see a value of $80 being
written to the paging register. Perhaps paging is from 1 to $80, or perhaps
there is more RAM than expected.

It's interesting to note that the addresses in page FD used by the software are
generally in the ranges $fd00-1f, $fd50-6f and $fde0-ff.

Looking at the third digit of each address (0, 1, 5, 6, e, f):

    0000
    0001
    0101
    0110
    1110
    1111

If bit 3 is set, bits 2 and 1 are also set.
If bit 1 is set, bit 2 is also set.

So, we do not need an address line for bit 2.

The routine at $9d31 in IC24-SK1 copies data from paged RAM to main RAM,
copying $fd00-$fd1c to $37d4-$37f0.

## Custom OSBYTE and OSWORD calls

IC24-SK1 provides a handler for unknown OSBYTE and OSWORD calls. These
implement OSWORD &81 which only has a documented implementation for the
Springboard, OSBYTE 7 and 8 which have existing meanings that are relevant,
and OSBYTE &40-&48 that are system dependent.

http://beebwiki.mdfs.net/OSWORDs
http://beebwiki.mdfs.net/OSBYTEs

OSWORD &81 accepts a parameter block, the first byte being the length of the
block itself. IC22 places this at $340b, then stores A at $340d, X at $3410 and
Y at $3411, using this format:

    <length> 0 A 0 0 X Y

A is used as the command/type of the call, with a value from 0-&36.

The commands perform the following functions:

    Command         Arguments           Function
    00              -                   Enable DUART channel A transmitter
    01              -                   Disable channel A transmitter
    02              -                   Enable channel A receiver
    03              -                   Disable channel A receiver
    04              -                   Reset channel A transmitter
    05              -                   Reset channel A receiver, flush FIFO
    06              -                   Reset channel A error status
    07              -                   Get DUART input ports status
    08              -                   Reset timer?
    09              -                   Read from channel A?
    0a              -                   Read channel A status
    0b              -                   Write to channel A
    0c              -                   ?
    0d              -                   Acknowledge interrupts?
    0e              -                   Initialise mode register for channel A?
    0f              -                   Similar to 0e
    10              -                   Enable DUART channel B transmitter
    11              -                   Disable channel B transmitter
    12              -                   Enable channel B receiver
    13              -                   Disable channel B receiver
    14              -                   Reset channel B transmitter
    15              -                   Reset channel B receiver, flush FIFO
    16              -                   Reset channel B error status
    17              -                   ?
    18              -                   Read channel B to $3f16 and $3f17, increment $3f15
    19              -                   Read channel B to $3f16, increment $3f15
    1a              X                   Write X (in $3f13) to channel B
    1b              -                   Similar to 0c
    1c              -                   
    1d
    1e
    1f
    20              -                   Initialise mode register for channel B?
    21                                  Write to VIA2 port A
    22                                  Read from VIA2 port B
    23              -                   Setup VIA2 interrupts?
    24              -                   Setup DUART interrupts?
    25              -                   Setup VIAs and DUART

OSBYTEs 7 and 8 appear to set the receive and send baud rates respectively for
the DUART.

## DUART



## Speech

According to page 54 of the BT Merlin M2105 Messaging Terminal User Guide, the
voice response message starts with, "This is a computer, please hold on... this
is" followed by a telephone number.

Looking at Appendix A of the Speech System User Guide, these words should map
to the following words and addresses:

    Word        Number          Address
    THIS        270 (0x10e)     0x3808
    IS          209 (0xd1)      0x1f57
    A           159 (0x9f)      0x0b5d
    COMPUTER    179 (0xb3)      0x140b
    PLEASE      241 (0xf1)      0x2bba
    HOLD        -               -
    ON          235 (0xeb)      0x2980
    OUR         -               -

The code at $a445 (0x2445) in IC24-SK1 appears to add an offset to values and
create a 9-bit value, suggesting something that could be used to encode the
numbers above, particularly for THIS.

Since the code adds 0x1f to each value apart from 0x61, subtracting 0x1f from
these numbers and searching the IC24-SK1 ROM for the first three values results
in a match at 0x2030 ($a030).

OLD is used instead of HOLD.

At $9f5e the routine uses the voice response option 0-4 (User Guide, p78) to
load a sequence of bits which specify which parts of a message to play.

    0       No voice response
    1       "Please try again"
    2       "Please try again after <time>"
    3       "Please try <telephone number>"
    4       "Please try <telephone number> after <time>"

The bit sequences are stored in an array at $a02b:

    Option  Bit sequence        Parts
    0       $00                 None
    1       $13 (10011)         0, 1, 4
    2       $1b (11011)         0, 1, 3, 4
    3       $15 (10101)         0, 2, 4
    4       $1d (11101)         0, 2, 3, 4

Part 0 is the greeting, "This is a computer, please hold on... this is" then
the telephone number of the M2105 then "Please try".
Part 1 is just the word, "again".
Part 2 is the telephone number of the M2105.
Part 3 is the word, "after", then at most 8 words to specify a time.
Part 4 is the phrase, "Thank you".

    Option  Parts       Result
    1       0, 1, 4     "... Please try again. Thank you."
    2       0, 1, 3, 4  "... Please try again after" <time>
    3       0, 2, 4     "... Please try" <number> "Thank you."
    4       0, 2, 3, 4  "... Please try" <number> "after" <time> "Thank you."

# Public UP5K/Pico v6 evidence subset

This is a documented subset of three pre-existing physical SEED → PROB reports,
not a replacement raw archive and not a new hardware run. The fixtures and
SOURCE-PINS.json are byte-identical to the sealed closure package.
PROVENANCE.json pins the original raw captures, sealed package and line selection.
Original report hashes remain in SOURCE-PINS.json; those private reports are not
required or distributed by this public verifier.

The excerpts preserve original numerical lines and their order/line endings.
USB identifiers, host/operator metadata and other private archive content are
withheld. The selected project-owned numerical data and verifier are published
under the repository MIT license. No third-party firmware or vendor data is
included.

From the repository root, using Python 3 standard library only:

    python3 -B verify_up5k_physical_evidence.py

The verifier checks the public manifest and source/fixture pins, exact six oracle
frames, request/response CRC16, sequence, READY samples, turnaround telemetry,
132 reported FIFO/shadow words, 18 snapshot hashes, postprint hashes, protocol
acknowledgments and final **software-reported** state. Its negative tests are in
tests/test_up5k_physical_evidence.py and run with the complete pytest suite.

PASS means the published excerpts reproduce the bounded three-record audit.
It does not authenticate physical provenance independently of the retained host
logs, measure electrical safety, read back installed FPGA fabric, qualify the
full oracle corpus or demonstrate quantum operation. Firmware-reported raw FIFO
and OE values are telemetry, not independent electrical measurements.

from __future__ import annotations

from src.spice_model import simulate_response


def main() -> None:
    print("CPC ngspice boundary-response verification")
    print()

    all_passed = True

    for x0 in (0, 1):
        for x3 in (0, 1):
            result = simulate_response(
                x0=x0,
                x3=x3,
#                 keep_netlist=True,
            )

            passed = result.decoded == result.expected
            all_passed = all_passed and passed

            print(
                f"x0={result.x0} "
                f"x3={result.x3} "
                f"expected={result.expected} "
                f"vout={result.output_voltage:.6f} V "
                f"decoded={result.decoded} "
                f"{'PASS' if passed else 'FAIL'}"
            )

    print()
    print("Complete continuation table:", "PASS" if all_passed else "FAIL")

    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

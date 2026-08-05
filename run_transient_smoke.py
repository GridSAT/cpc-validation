from __future__ import annotations

from src.transient_analysis import simulate_transient_response


def format_optional_time(value: float | None) -> str:
    if value is None:
        return "not reached"

    return f"{1000.0 * value:.6f} ms"


def main() -> None:
    print("CPC RC transient-analysis smoke test")
    print()

    all_passed = True

    for x0 in (0, 1):
        for x3 in (0, 1):
            response = simulate_transient_response(
                x0=x0,
                x3=x3,
                resistance_kohm=10.0,
                capacitance_uf=1.0,
                end_time_ms=150.0,
            )

            passed = response.decoded == response.expected
            all_passed = all_passed and passed

            print(
                f"x0={response.x0} "
                f"x3={response.x3} "
                f"expected={response.expected} "
                f"final={response.final_voltage:.6f} V "
                f"decoded={response.decoded} "
                f"rise={format_optional_time(response.rise_time_seconds)} "
                f"settling={format_optional_time(response.settling_time_seconds)} "
                f"samples={len(response.samples)} "
                f"{'PASS' if passed else 'FAIL'}"
            )

    print()
    print(
        "Transient smoke test:",
        "PASS" if all_passed else "FAIL",
    )

    if not all_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

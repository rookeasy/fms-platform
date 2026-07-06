import argparse

from scripts.seed_fuzion_projects import seed_fuzion_projects


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the retired SOHO Phase I compatibility entrypoint.")
    parser.add_argument("--cleanup-soho", action="store_true", help="Compatibility flag; Fuzion-only seeding handles cleanup.")
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    result = seed_fuzion_projects()
    print(
        "SOHO property seed has been retired; Fuzion active/completed projects only: "
        f"{result['upserted']} upserted, {result['archived']} archived"
    )

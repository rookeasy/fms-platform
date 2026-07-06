import argparse

from scripts.seed_fuzion_projects import seed_fuzion_projects


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the Fuzion reference portfolio records.")
    parser.add_argument("--cleanup-placeholders", action="store_true", help="Compatibility flag; Fuzion-only seeding handles cleanup.")
    parser.add_argument("--cleanup-duplicates", action="store_true", help="Compatibility flag; Fuzion-only seeding handles cleanup.")
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
    result = seed_fuzion_projects()
    print(
        "Reference portfolio seed now uses Fuzion active/completed projects only: "
        f"{result['upserted']} upserted, {result['archived']} archived"
    )

from scripts.seed_fuzion_projects import seed_fuzion_projects


if __name__ == "__main__":
    result = seed_fuzion_projects()
    print(
        "SOHO closeout seed has been retired; Fuzion active/completed projects only: "
        f"{result['upserted']} upserted, {result['archived']} archived"
    )

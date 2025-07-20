from pydantic import BaseModel

class EpsteinFiles(BaseModel):
    incriminating_records: list[str]
    non_incriminating_records: list[str]

if __name__ == "__main__":
    all_files = EpsteinFiles(
        incriminating_records=["birthday letter with nakey doodle"],
        non_incriminating_records=["Grand Jury record"]
    )

    for_public_release = all_files.model_dump(
        # Oopsie! Typo!
        exclude={"incrimnating_records"}
    )
    print(for_public_release)
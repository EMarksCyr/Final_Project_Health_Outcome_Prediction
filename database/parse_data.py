from data_encoding import (
    get_encoding_table,
    get_field,
)

import zipfile
import glob
from pathlib import Path
import os
import time
import csv
from sqlalchemy import create_engine
from getpass import getpass

_TMP_DIR = Path("./tmp/")

user_id = 0
question_id_cache = {}  # field:question_id


def decode_line(line):
    d = {}
    for field in get_encoding_table():
        d[field.name] = get_field(line, field)
    return d


def db_insert(user_answers):
    print(list(user_answers.items())[0])


def extract_data(process_entry_func):
    _TMP_DIR.mkdir(parents=True, exist_ok=True)
    for fpath in glob.glob("./data/**/*.zip", recursive=True):
        extract_path = ""
        with zipfile.ZipFile(fpath, "r") as zip_ref:
            filename = os.path.basename(fpath)
            filename = filename[filename.rfind(".")]
            extract_path = _TMP_DIR / filename
            zip_ref.extractall(extract_path)

        for data_file in glob.glob(str(extract_path / "*")):
            with open(data_file, "r") as f:
                for line in f:
                    process_entry_func(decode_line(line))


if __name__ == "__main__":
    t0 = time.time()

    # TODO: add back in
    password = getpass("Enter database password")
    db = create_engine(f"postgresql://postgres:{password}@localhost:5432/BRFSSAnalysis")

    db.execute("TRUNCATE user_answers")

    def db_get_question_value_info_from_answer(question_id, question_answer):
        result = db.execute(
            """SELECT * FROM question_values 
            WHERE 
                question_id = %s AND 
                (value = %s OR 
                    (value_end IS NOT NULL AND value <= %s AND %s <= value_end))
            """,
            (question_id, question_answer, question_answer, question_answer),
        )
        return result.fetchall()

    def is_user_answer_hidden(question_id, question_answer):
        """True if the given user answer correponds to a hidden question value.

        NOTE: User answers that have a value (ie. are not NULL or blank) can correspond to a hidden
        question value.
        """
        # If value is not in q vals and hidden is in q vals then is hidden answer
        value_rows = db_get_question_value_info_from_answer(
            question_id, question_answer
        )

        if not value_rows:
            # Check for HIDDEN value
            result = db.execute(
                "SELECT * FROM question_values WHERE question_id = %s AND value IS NULL",
                (question_id,),
            )
            rows = result.fetchall()
            if len(rows) > 0:
                assert (
                    len(rows) == 1
                )  # Should be exactly one HIDDEN valid value per question

                # There is a valid HIDDEN value
                return True

        return False

    def insert_answers_into_db(entry):
        global user_id
        global question_id_cache

        for question in entry.items():
            question_label = question[0]
            question_answer = question[1]

            # look up question id by label
            question_id = -1
            if question_label in question_id_cache:
                question_id = question_id_cache[question_label]

            else:
                result = db.execute(
                    """SELECT id FROM question_info WHERE var_name LIKE %s""",
                    (question_label,),
                )
                rows = result.fetchall()
                assert len(rows) == 1  # only one q per answer
                question_id = rows[0][0]
                question_id_cache[question_label] = question_id

            # insert answer by question id
            db.execute(
                "INSERT INTO user_answers(user_id, question_id, val) VALUES (%s, %s, %s)",
                (user_id, question_id, question_answer),
            )

            # bonus: confirm the answer is in the question_values table
            print(f"qid={question_id}, qa={question_answer}")
            rows = db_get_question_value_info_from_answer(question_id, question_answer)
            print(rows)
            if rows:
                # Must be exactly one valid question answer match
                assert len(rows) == 1
            else:
                # If no corresponding valid value, then HIDDEN must be a valid value
                assert is_user_answer_hidden(question_id, question_answer)

        # Move to next user entry
        # NOTE: All answers in an entry corresponds to one individual
        user_id += 1

    extract_data(insert_answers_into_db)

    """
    with open("data.csv", "w", newline="") as f:
        headers = []
        for field in get_encoding_table():
            headers.append(field.name)

        # CSV writing
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        def write_csv_row(entry):
            writer.writerow(entry)
        extract_data(write_csv_row)
    """

    t1 = time.time()

    print(f"Elapsed time: {t1 - t0}s")

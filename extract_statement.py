import pymupdf
import pandas as pd
import re

vg = pymupdf.open("vig_nov2026_eng.pdf")

startp = 726
endp = 738

results = []

for pnum in range(startp - 1, endp):
    pg = vg[pnum]
    text = page.get_text("text")

    # 1. Extract candidate name from:

    # "I, [name], hereby declare..."

    name_match = re.search(

        r"I,\s*(.+?),\s*hereby declare",

        text,

        re.IGNORECASE

    )

    candidate_name = name_match.group(1).strip() if name_match else None

    # 2. Extract district number from:

    # "FOR MEMBER OF CITY COUNCIL, DISTRICT [num]"

    district_match = re.search(

        r"FOR\s+MEMBER\s+OF\s+CITY\s+COUNCIL,\s*DISTRICT\s+(\d+)",

        text,

        re.IGNORECASE

    )

    district = district_match.group(1) if district_match else None

    # 3. Extract the text following "9."

    # Stop before the next numbered item, if there is one.

    statement_match = re.search(

        r"(?:^|\n)\s*9\.\s*(.*?)(?=\n\s*10\.\s|\Z)",

        text,

        re.DOTALL

    )

    statement = statement_match.group(1).strip() if statement_match else None

    # Clean up line breaks and repeated whitespace

    if statement:

        statement = re.sub(r"\s+", " ", statement)

    results.append({

        "candidate_name": candidate_name,

        "district": district,

        "statement": statement,

        "pdf_page": page_number + 1

    })

# Save results to a spreadsheet-friendly CSV

df = pd.DataFrame(results)

df.to_csv("candidate_statements.csv", index=False)

# Display the results so you can check whether extraction worked

print(df.to_string(index=False))

# Flag any pages where something wasn't found

for row in results:

    if not row["candidate_name"] or not row["district"] or not row["statement"]:

        print(f"\nCHECK PAGE {row['pdf_page']}:")

        if not row["candidate_name"]:

            print("  - Candidate name not found")

        if not row["district"]:

            print("  - District number not found")

        if not row["statement"]:

            print("  - Statement not found")
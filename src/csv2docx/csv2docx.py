import csv
from pathlib import Path

from mailmerge import MailMerge


def create_output_folder(output_path: str) -> Path:
    """Creates a path to store output data if it does not exists.
    Args:
        path: the path from user in any format (relative, absolute, etc.)
    Returns:
        A path to store output data.
    """
    path = Path(output_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def create_unique_name(filename: str, path: Path) -> Path:
    """Creates a unique filename for specified path.
    Args:
        filename: the name of file to create
        path: the path where the file is stored
    Returns:
        An absolute path with directory.
    """
    filename = filename.strip() + ".docx"
    filepath = path / filename
    if filepath.exists():
        # Count available files with same name
        counter = len(list(path.glob(f"{filepath.stem}*docx"))) + 1
        filepath = path / f"{filepath.stem}_{counter}.docx"
    return filepath


def convert(
    data: str, template: str, name: str, path: str = "output", delimiter: str = ";"
) -> None:
    print("Getting .docx template and .csv data files ...")

    with open(data, "rt") as csvfile:
        csvdict = csv.DictReader(csvfile, delimiter=delimiter)
        csv_headers = csvdict.fieldnames
        if csv_headers and name not in csv_headers:
            print("Column name not found. Please enter valid column name")
            exit(1)
        docx = MailMerge(template)
        docx_mergefields = docx.get_merge_fields()

        print(f"DOCX fields : {docx_mergefields}")
        print(f"CSV field   : {csv_headers}")

        # see if all fields are accounted for in the .csv header
        column_in_data = set(docx_mergefields) - set(csv_headers)
        if len(column_in_data) > 0:
            print(f"{column_in_data} is in the word document, but not csv.")
            return

        print("All fields are present in your csv. Generating Word docs ...")
        output_path = create_output_folder(path)

        for row in csvdict:
            # Must create a new MailMerge for each file
            docx = MailMerge(template)
            single_document = {key: row[key] for key in docx_mergefields}
            docx.merge_templates([single_document], separator="page_break")
            filename = create_unique_name(row[name], output_path)
            docx.write(filename)

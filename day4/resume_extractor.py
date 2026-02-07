import os
import PyPDF2
from docx import Document


def pdf_to_md(filepath):
    """reads pdf files and return markdown texts"""
    md_output = f"## Document: {os.path.basename(filepath)} \n\n"
    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    md_output += f"### Page {i+1}\n{page_text}\n\n"

        return md_output
    except Exception as e:
        return f"got error: {e}"


def docx_to_md(filepath):
    """Reads word or document files and return markdown text"""
    md_output = f"## Document: {os.path.basename(filepath)} \n\n"
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            if para.text.strip():
                md_output += f"{para.text}\n\n"

        return md_output
    except Exception as e:
        return f"got error: {e}"


## process Resumes ##
def process_resumes(input_folder: str) -> list:
    """Iterate through each resumes which exist in the folder, and
    extract the content in list of markdowns
    """

    extracted_docs = []

    # to list content of any directory/forlder we use os.listdir(<path or name of folder>)

    dirlist = os.listdir(input_folder)

    for filename in dirlist:
        # step 1: create filepath to read
        filepath = os.path.join(input_folder, filename)  # "./resumes/Anas_Resumes.pdf"

        # step 2: extract extension
        ext = filename.lower().split(".")[-1]  # .split() returns list of string

        if ext == "pdf":
            content = pdf_to_md(filepath)
            extracted_docs.append(content)
        elif ext in ["docx", "doc"]:
            content = docx_to_md(filepath)
            extracted_docs.append(content)
        else:
            print("unsupported extension file found")

    return extracted_docs


### configurations ###
input_folder = "./Resumes"



## Function to extract the files ##
if __name__ == "__main__":
    if not os.path.exists(input_folder):
        print("file or folder does not exist")
    else:
        markdown_resumes = process_resumes(input_folder)

        if markdown_resumes:
            print("---- sample output ----")
            print(markdown_resumes[0])


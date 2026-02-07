import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


### Confgurations ###
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROK_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROK_API_KEY:
    print("WARNING: GROQ_API_KEY not found in environment variables.")

output_file = "resume_data.json"


SYSTEM_PROMPT = """
You are a smart ATS and Resume Analyzer system.
- **You will return the extracted information in a structured JSON format**.
- You Extract skills, experience, education, certifications, and other relevant information from the resumes.
- You analyze the resumes and provide insights on the candidate's Profile and make your on strict un biased suggestions.
- You will be given resumes in markdown format, and you have to extract the following information from it:
    1. Name of the candidate
    2. Contact Information (email, phone number)
    3. Skills (both technical and soft skills)
    4. Work Experience (company name, role, duration, key responsibilities)
    5. Education (degree, institution, graduation year)
    6. Certifications (name of certification, issuing organization, date of issue)
    7. Summary or Objective statement (if available)
- Here is an example of what you need to return:
{
    "name": "John Doe",
    "contact_info": {
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567"
    },
    "skills": [
        "Python",
        "JavaScript",
        "Project Management"
    ],
    "work_experience": [
        {
            "company": "Tech Solutions Inc.",
            "role": "Senior Software Engineer",
            "duration": "2020 - 2023",
            "responsibilities": [
                "Led development of web applications using Python and Django.",
                "Mentored junior developers and conducted code reviews."
            ]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of Technology",
            "graduation_year": 2020
        }
    ],
    "certifications": [
        {
            "name": "AWS Certified Developer",
            "issuing_organization": "Amazon Web Services",
            "date_of_issue": "2021-06-15"
        }
    ],
    "summary_or_objective_statement": [
        {
            "type": "summary",
            "content": [
                {
                    "__text__": [
                        "**Summary:** John is a senior software engineer with over 3 years of experience in building scalable web applications. He has expertise in Python, JavaScript, and cloud technologies."
                    ]
                }
            ]
        }
    ]
}
"""


"""
- Take Input of MarkDowns
- LLM interaction
- Create JSon from LLM result
"""


def extract_info_from_llm(md_content: str) -> dict:
    """This function will take markdown content as input, and return the extracted information in structured json format"""

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = SYSTEM_PROMPT

    user_prompt = f"""
    Resume Content: 
    {md_content}
    """

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    
    try:
        response = requests.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        response_data = response.json()
        
        print("LLM Response:")
        print(json.dumps(response_data, indent=2))

        llm_output = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

        structured_data = json.loads(llm_output)

        return structured_data
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        if e.response is not None:
             print(f"Error Response Body: {e.response.text}")
        return {}
    except json.JSONDecodeError as e:
        print(f"JSON decoding failed: {e}")
        return {}


def save_to_json(data: list):
    """This function will save the analyzed output in json file"""

    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Data successfully saved to {output_file}")
    except IOError as e:
        print(f"File I/O error: {e}")


def analyzing_pipeline(md_list: list):
    """This function will take list of markdowns as input, and return the analyzed output in json format"""

    final_data = []

    for i, md in enumerate(md_list):
        print(f"Processing Resume {i+1}...")

        structured_data = extract_info_from_llm(md)

        if structured_data:
            final_data.append(structured_data)

    save_to_json(final_data)

from app.services.parser_service import (
    normalize_text,
    repair_hyphenated_line_breaks,
)
from app.services.section_service import (
    detect_section_heading,
    detect_sections,
)
from app.services.structured_service import (
    extract_certifications,
    extract_email,
    extract_phone,
    extract_profile_urls,
    extract_skill_categories,
)


class TestParserPreprocessing:
    def test_normalize_supported_bullet_symbols(self):
        text = (
            "\u2022 First bullet\n"
            "\u25cf Second bullet\n"
            "\u25aa Third bullet\n"
            "\u25e6 Fourth bullet\n"
            "\uf0b7 Fifth bullet"
        )

        result = normalize_text(text)

        assert result.splitlines() == [
            "\u2022 First bullet",
            "\u2022 Second bullet",
            "\u2022 Third bullet",
            "\u2022 Fourth bullet",
            "\u2022 Fifth bullet",
        ]

    def test_repair_common_prefix_line_break(self):
        text = "Vendor re-\nquirements were validated."

        result = repair_hyphenated_line_breaks(text)

        assert result == "Vendor requirements were validated."

    def test_preserve_true_hyphenated_word(self):
        text = "Supports closed-\nloop payment systems."

        result = repair_hyphenated_line_breaks(text)

        assert result == "Supports closed-loop payment systems."

    def test_normalize_whitespace_and_remove_empty_lines(self):
        text = "Python    FastAPI\n\n   PostgreSQL   "

        result = normalize_text(text)

        assert result == "Python FastAPI\nPostgreSQL"


class TestSectionDetection:
    def test_detect_known_section_heading(self):
        assert (
            detect_section_heading("PROFESSIONAL SUMMARY")
            == "professional_summary"
        )

        assert (
            detect_section_heading("Technical Skills:")
            == "technical_skills"
        )

        assert (
            detect_section_heading("PERSONAL PROJECTS")
            == "projects"
        )

    def test_unknown_heading_returns_none(self):
        assert detect_section_heading("SOME RANDOM HEADING") is None

    def test_detect_multiple_resume_sections(self):
        text = """SOHAN CHHANGANI
Senior Embedded Software Engineer
PROFESSIONAL SUMMARY
Embedded software engineer with payment experience.
TECHNICAL SKILLS
Languages: C, Python
PROFESSIONAL EXPERIENCE
Developed payment applications.
EDUCATION
Bachelor of Engineering
"""

        result = detect_sections(text)

        assert result == {
            "professional_summary": (
                "Embedded software engineer with payment experience."
            ),
            "technical_skills": "Languages: C, Python",
            "professional_experience": (
                "Developed payment applications."
            ),
            "education": "Bachelor of Engineering",
        }

    def test_text_before_first_section_is_ignored(self):
        text = """SOHAN CHHANGANI
Senior Embedded Software Engineer
TECHNICAL SKILLS
Languages: Python
"""

        result = detect_sections(text)

        assert result == {
            "technical_skills": "Languages: Python",
        }


class TestStructuredExtraction:
    def test_extract_email(self):
        text = "Contact me at engineer@example.com"

        assert extract_email(text) == "engineer@example.com"

    def test_extract_email_returns_none_when_missing(self):
        assert extract_email("No email here") is None

    def test_extract_phone(self):
        text = "Phone: +91 9876543210"

        assert extract_phone(text) == "+91 9876543210"

    def test_extract_profile_urls(self):
        text = (
            "https://linkedin.com/in/test-user\n"
            "https://github.com/test-user"
        )

        result = extract_profile_urls(text)

        assert result == {
            "linkedin": "https://linkedin.com/in/test-user",
            "github": "https://github.com/test-user",
        }

    def test_extract_multiline_skill_format(self):
        text = """Programming Languages:
C, Python, Java, Bash, C++
Platforms & Tools:
Git, Docker, Linux
"""

        result = extract_skill_categories(text)

        assert result == {
            "programming_languages": [
                "C",
                "Python",
                "Java",
                "Bash",
                "C++",
            ],
            "platforms_and_tools": [
                "Git",
                "Docker",
                "Linux",
            ],
        }

    def test_extract_inline_bullet_skill_format(self):
        text = (
            "Languages: C \u2022 Python \u2022 Bash \u2022 Java\n"
            "Backend: FastAPI \u2022 PostgreSQL \u2022 Docker"
        )

        result = extract_skill_categories(text)

        assert result == {
            "languages": [
                "C",
                "Python",
                "Bash",
                "Java",
            ],
            "backend": [
                "FastAPI",
                "PostgreSQL",
                "Docker",
            ],
        }

    def test_filter_certification_placeholder(self):
        text = (
            "Relevant certifications will be added "
            "as they are completed and verified."
        )

        assert extract_certifications(text) == []

    def test_filter_standalone_urls_from_certifications(self):
        text = """https://linkedin.com/in/test-user
https://github.com/test-user
https://example.com/portfolio
"""

        assert extract_certifications(text) == []

    def test_preserve_real_certifications(self):
        text = """Linux Kernel Fundamentals (Linux Foundation)
Python Professional Certification
https://github.com/test-user
Relevant certifications will be added later.
"""

        result = extract_certifications(text)

        assert result == [
            "Linux Kernel Fundamentals (Linux Foundation)",
            "Python Professional Certification",
        ]

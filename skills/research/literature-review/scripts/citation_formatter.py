#!/usr/bin/env python3
"""
Citation Formatter Utility for Literature Reviews

Converts between common citation formats (APA, Chicago, IEEE, Nature)
and helps format citations consistently.

Usage:
    python citation_formatter.py --input input.csv --output output.csv --format apa
    python citation_formatter.py --doi 10.1038/nature12373 --format chicago
"""

import argparse
import json


class Citation:
    """Represents a single citation with metadata."""

    def __init__(self, **kwargs):
        self.authors = kwargs.get("authors", [])
        self.year = kwargs.get("year", "")
        self.title = kwargs.get("title", "")
        self.journal = kwargs.get("journal", "")
        self.volume = kwargs.get("volume", "")
        self.issue = kwargs.get("issue", "")
        self.pages = kwargs.get("pages", "")
        self.doi = kwargs.get("doi", "")
        self.url = kwargs.get("url", "")
        self.publication_type = kwargs.get(
            "type", "journal"
        )  # journal, book, chapter, web, conference

    def to_apa(self) -> str:
        """Format citation in APA style."""
        authors_str = self._format_authors_apa()

        citation = f"{authors_str} ({self.year}). {self.title}. "

        if self.publication_type == "journal":
            citation += f"{self.journal}, {self.volume}({self.issue}), {self.pages}."
        elif self.publication_type == "book":
            citation += f"{self.journal}."

        if self.doi:
            citation += f" https://doi.org/{self.doi}"
        elif self.url:
            citation += f" {self.url}"

        return citation

    def to_chicago(self) -> str:
        """Format citation in Chicago (author-date) style."""
        authors_str = self._format_authors_chicago()

        citation = (
            f'{authors_str}. "{self.title}." {self.journal} {self.volume}, '
            f"no. {self.issue} ({self.year}): {self.pages}."
        )

        if self.doi:
            citation += f" https://doi.org/{self.doi}"
        elif self.url:
            citation += f" {self.url}"

        return citation

    def to_ieee(self) -> str:
        """Format citation in IEEE style."""
        authors_str = self._format_authors_ieee()

        citation = (
            f'{authors_str}, "{self.title}," {self.journal}, vol. {self.volume}, '
            f"no. {self.issue}, pp. {self.pages}, {self.year}"
        )

        if self.doi:
            citation += f", doi: {self.doi}"

        citation += "."

        return citation

    def to_nature(self) -> str:
        """Format citation in Nature style."""
        authors_str = self._format_authors_nature()

        citation = (
            f"{authors_str} {self.title}. {self.journal} {self.volume}, {self.pages} ({self.year})."
        )

        if self.doi:
            citation += f" https://doi.org/{self.doi}"

        return citation

    def _format_authors_apa(self) -> str:
        """Format authors for APA style: Last, First & Last, First."""
        if not self.authors:
            return ""

        if len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} & {self.authors[1]}"
        elif len(self.authors) <= 5:
            return ", ".join(self.authors[:-1]) + f", & {self.authors[-1]}"
        else:
            return f"{self.authors[0]} et al."

    def _format_authors_chicago(self) -> str:
        """Format authors for Chicago style: Last, First and Last, First."""
        if not self.authors:
            return ""

        if len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        elif len(self.authors) <= 5:
            return ", ".join(self.authors[:-1]) + f", and {self.authors[-1]}"
        else:
            return f"{self.authors[0]} et al."

    def _format_authors_ieee(self) -> str:
        """Format authors for IEEE style: Initials Last."""
        if not self.authors:
            return ""

        # Simplified - would need to parse first names from full author format
        if len(self.authors) > 3:
            return f"{self.authors[0]} et al."
        else:
            return " and ".join(self.authors)

    def _format_authors_nature(self) -> str:
        """Format authors for Nature style: Last, F. & Last, F."""
        # Simplified formatting
        return ", ".join(self.authors[:3]) + (" et al." if len(self.authors) > 3 else "")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "authors": self.authors,
            "year": self.year,
            "title": self.title,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "doi": self.doi,
            "url": self.url,
            "type": self.publication_type,
        }


class CitationFormatter:
    """Main utility for formatting citations."""

    def __init__(self):
        self.citations = []

    def add_citation(self, citation: Citation):
        """Add a citation to the collection."""
        self.citations.append(citation)

    def load_from_csv(self, filename: str) -> list[Citation]:
        """Load citations from CSV file (simplified)."""
        citations = []
        try:
            import csv

            with open(filename) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    authors = [a.strip() for a in row.get("authors", "").split(";")]
                    citation = Citation(
                        authors=authors,
                        year=row.get("year", ""),
                        title=row.get("title", ""),
                        journal=row.get("journal", ""),
                        volume=row.get("volume", ""),
                        issue=row.get("issue", ""),
                        pages=row.get("pages", ""),
                        doi=row.get("doi", ""),
                        url=row.get("url", ""),
                        type=row.get("type", "journal"),
                    )
                    citations.append(citation)
        except ImportError:
            print("CSV module not available")
        except FileNotFoundError:
            print(f"File {filename} not found")

        return citations

    def save_to_json(self, citations: list[Citation], filename: str):
        """Save citations to JSON file."""
        data = [c.to_dict() for c in citations]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(citations)} citations to {filename}")

    def format_batch(self, citations: list[Citation], output_format: str = "apa") -> list[str]:
        """Format multiple citations in specified format."""
        format_method = f"to_{output_format.lower()}"
        results = []

        for citation in citations:
            if hasattr(citation, format_method):
                results.append(getattr(citation, format_method)())
            else:
                print(f"Unknown format: {output_format}")
                return []

        return results


def main():
    parser = argparse.ArgumentParser(description="Citation Formatter for Literature Reviews")

    parser.add_argument("--input", help="Input CSV file with citations")
    parser.add_argument("--output", help="Output file for formatted citations")
    parser.add_argument(
        "--format",
        default="apa",
        choices=["apa", "chicago", "ieee", "nature"],
        help="Citation format",
    )
    parser.add_argument("--doi", help="Format a single citation from DOI")
    parser.add_argument("--list", action="store_true", help="List supported formats")

    args = parser.parse_args()

    if args.list:
        print("Supported citation formats:")
        print("  - apa (American Psychological Association)")
        print("  - chicago (Chicago Manual of Style)")
        print("  - ieee (IEEE Style)")
        print("  - nature (Nature/Science Style)")
        return

    formatter = CitationFormatter()

    if args.input:
        print(f"Loading citations from {args.input}...")
        citations = formatter.load_from_csv(args.input)

        if citations:
            print(f"Loaded {len(citations)} citations")
            formatted = formatter.format_batch(citations, args.format)

            if args.output:
                with open(args.output, "w") as f:
                    for i, formatted_cite in enumerate(formatted):
                        f.write(f"{i + 1}. {formatted_cite}\n")
                print(f"Formatted citations saved to {args.output}")
            else:
                print(f"\nFormatted citations ({args.format.upper()}):\n")
                for i, formatted_cite in enumerate(formatted, 1):
                    print(f"{i}. {formatted_cite}\n")

    elif args.doi:
        print(f"DOI: {args.doi}")
        print(
            "Note: Full metadata retrieval would require API access to CrossRef or similar service"
        )
        print("This is a placeholder for demonstration")

    else:
        print("Example usage:")
        print("  python citation_formatter.py --input citations.csv \\")
        print("         --output formatted.txt --format apa")
        print("  python citation_formatter.py --list")


if __name__ == "__main__":
    main()

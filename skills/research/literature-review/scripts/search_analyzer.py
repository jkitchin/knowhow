#!/usr/bin/env python3
"""
Search Log Analyzer for Literature Reviews

Analyzes search patterns, coverage, and convergence to guide iterative refinement.

Usage:
    python search_analyzer.py --log search_log.json --analyze coverage
    python search_analyzer.py --log search_log.json --report summary
"""

import argparse
import json
from collections import defaultdict


class SearchLog:
    """Represents a literature review search log."""

    def __init__(self):
        self.searches = []
        self.total_papers = 0
        self.unique_papers = set()

    def add_search(self, search_record: dict):
        """Add a search record."""
        self.searches.append(search_record)

    def load_from_json(self, filename: str) -> bool:
        """Load search log from JSON file."""
        try:
            with open(filename) as f:
                data = json.load(f)
                if isinstance(data, list):
                    for record in data:
                        self.add_search(record)
                else:
                    self.add_search(data)
            return True
        except FileNotFoundError:
            print(f"File {filename} not found")
            return False
        except json.JSONDecodeError:
            print(f"Invalid JSON in {filename}")
            return False

    def get_coverage_metrics(self) -> dict:
        """Calculate coverage metrics."""
        total_results = sum(s.get("results", 0) for s in self.searches)
        total_retained = sum(s.get("retained", 0) for s in self.searches)
        avg_pass_rate = (total_retained / total_results * 100) if total_results > 0 else 0

        return {
            "total_searches": len(self.searches),
            "total_results": total_results,
            "total_retained": total_retained,
            "average_pass_rate": round(avg_pass_rate, 1),
            "databases_searched": len(set(s.get("database", "") for s in self.searches)),
        }

    def get_database_coverage(self) -> dict:
        """Analyze coverage by database."""
        coverage = defaultdict(lambda: {"searches": 0, "results": 0, "retained": 0})

        for search in self.searches:
            db = search.get("database", "Unknown")
            coverage[db]["searches"] += 1
            coverage[db]["results"] += search.get("results", 0)
            coverage[db]["retained"] += search.get("retained", 0)

        return dict(coverage)

    def get_convergence_analysis(self) -> dict:
        """Analyze search convergence (diminishing returns)."""
        convergence = {
            "searches": [],
            "new_papers_trend": [],
            "retention_rate_trend": [],
            "convergence_status": "Not converged",
        }

        for i, search in enumerate(self.searches, 1):
            new_papers = search.get("retained", 0)
            retention_rate = (
                (new_papers / search.get("results", 1) * 100) if search.get("results", 0) > 0 else 0
            )

            convergence["searches"].append(f"Search {i}")
            convergence["new_papers_trend"].append(new_papers)
            convergence["retention_rate_trend"].append(round(retention_rate, 1))

        # Simple convergence check: last 3 searches showing <10% new papers
        if len(convergence["new_papers_trend"]) >= 3:
            last_three_avg = sum(convergence["new_papers_trend"][-3:]) / 3
            if last_three_avg < 5:  # Less than 5 new papers on average in last 3 searches
                convergence["convergence_status"] = "Converged (diminishing returns)"
            elif last_three_avg < 15:
                convergence["convergence_status"] = "Approaching convergence"

        return convergence

    def get_temporal_trends(self) -> dict:
        """Analyze temporal trends in searching."""
        trends = {"searches_over_time": [], "results_progression": [], "cumulative_papers": 0}

        cumulative = 0
        for i, search in enumerate(self.searches, 1):
            results = search.get("results", 0)
            retained = search.get("retained", 0)
            cumulative += retained

            trends["searches_over_time"].append(
                {
                    "search": f"Search {i}",
                    "date": search.get("date", "Unknown"),
                    "results": results,
                    "retained": retained,
                }
            )
            trends["results_progression"].append(cumulative)

        trends["cumulative_papers"] = cumulative
        return trends

    def recommend_next_steps(self) -> list[str]:
        """Generate recommendations for next steps."""
        recommendations = []

        metrics = self.get_coverage_metrics()
        convergence = self.get_convergence_analysis()

        # Check if converged
        if "Converged" in convergence["convergence_status"]:
            recommendations.append(
                "✓ Search appears to have converged - likely found most relevant papers"
            )
            recommendations.append("→ Proceed to full-text screening and data extraction")
        elif "Approaching" in convergence["convergence_status"]:
            recommendations.append("→ Continue 1-2 more targeted searches to confirm convergence")
            recommendations.append("→ Focus on identified gaps or methodological variations")
        else:
            recommendations.append("→ Continue iterative searching with refined strategies")

        # Check database coverage
        db_coverage = self.get_database_coverage()
        if len(db_coverage) < 3:
            recommendations.append(
                "→ Expand to additional databases (currently using only "
                + str(len(db_coverage))
                + " databases)"
            )

        # Check pass rate
        if metrics["average_pass_rate"] < 10:
            recommendations.append(
                "⚠ Low pass rate (<10%) - consider refining search terms or criteria"
            )
        elif metrics["average_pass_rate"] > 30:
            recommendations.append("✓ Good pass rate (>30%) - search strategy is well-targeted")

        if not recommendations:
            recommendations.append("Continue with current search strategy")

        return recommendations

    def generate_report(self, format: str = "text") -> str:
        """Generate comprehensive search report."""
        report = []

        report.append("=" * 60)
        report.append("LITERATURE REVIEW SEARCH LOG ANALYSIS")
        report.append("=" * 60)

        # Coverage metrics
        metrics = self.get_coverage_metrics()
        report.append("\n📊 COVERAGE METRICS")
        report.append(f"  Total searches: {metrics['total_searches']}")
        report.append(f"  Databases: {metrics['databases_searched']}")
        report.append(f"  Total results: {metrics['total_results']}")
        report.append(f"  Papers retained: {metrics['total_retained']}")
        report.append(f"  Average pass rate: {metrics['average_pass_rate']}%")

        # Database coverage
        report.append("\n🗄️  DATABASE COVERAGE")
        db_coverage = self.get_database_coverage()
        for db, stats in sorted(db_coverage.items()):
            pass_rate = (stats["retained"] / stats["results"] * 100) if stats["results"] > 0 else 0
            report.append(f"  {db}:")
            report.append(f"    - Searches: {stats['searches']}")
            report.append(f"    - Results: {stats['results']}")
            report.append(f"    - Retained: {stats['retained']} ({pass_rate:.1f}%)")

        # Convergence analysis
        report.append("\n📈 CONVERGENCE ANALYSIS")
        convergence = self.get_convergence_analysis()
        report.append(f"  Status: {convergence['convergence_status']}")
        report.append("  Papers by search:")
        for search, new_papers in zip(convergence["searches"], convergence["new_papers_trend"]):
            report.append(f"    {search}: {new_papers} papers retained")

        # Temporal trends
        report.append("\n⏱️  TEMPORAL TRENDS")
        temporal = self.get_temporal_trends()
        report.append(f"  Total papers (cumulative): {temporal['cumulative_papers']}")

        # Recommendations
        report.append("\n💡 RECOMMENDATIONS")
        for rec in self.recommend_next_steps():
            report.append(f"  {rec}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Search Log Analyzer for Literature Reviews")

    parser.add_argument("--log", help="Search log JSON file")
    parser.add_argument(
        "--analyze",
        choices=["coverage", "convergence", "trends"],
        help="Type of analysis to perform",
    )
    parser.add_argument("--report", choices=["summary", "detailed"], help="Generate report")
    parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    if not args.log:
        print("Example usage:")
        print("  python search_analyzer.py --log search_log.json --report summary")
        print("  python search_analyzer.py --log search_log.json --analyze coverage")
        print("\nExample JSON structure:")
        print(
            json.dumps(
                {
                    "database": "PubMed",
                    "date": "2025-01-15",
                    "query": '"machine learning" AND "medical imaging"',
                    "results": 2847,
                    "retained": 456,
                    "notes": "Good initial search",
                },
                indent=2,
            )
        )
        return

    # Load search log
    log = SearchLog()
    if not log.load_from_json(args.log):
        return

    print(f"Loaded {len(log.searches)} searches from {args.log}\n")

    # Generate report
    if args.report:
        report = log.generate_report(args.report)
        print(report)

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"\nReport saved to {args.output}")

    # Specific analyses
    elif args.analyze == "coverage":
        print("DATABASE COVERAGE ANALYSIS")
        print("-" * 40)
        coverage = log.get_database_coverage()
        for db, stats in sorted(coverage.items()):
            pass_rate = (stats["retained"] / stats["results"] * 100) if stats["results"] > 0 else 0
            print(f"{db}: {stats['retained']}/{stats['results']} ({pass_rate:.1f}%)")

    elif args.analyze == "convergence":
        print("CONVERGENCE ANALYSIS")
        print("-" * 40)
        convergence = log.get_convergence_analysis()
        print(f"Status: {convergence['convergence_status']}\n")
        for search, papers in zip(convergence["searches"], convergence["new_papers_trend"]):
            print(f"{search}: {papers} papers")

    elif args.analyze == "trends":
        print("TEMPORAL TRENDS")
        print("-" * 40)
        temporal = log.get_temporal_trends()
        cumulative = 0
        for item in temporal["searches_over_time"]:
            cumulative += item["retained"]
            print(f"{item['search']} ({item['date']}): +{item['retained']} → {cumulative} total")


if __name__ == "__main__":
    main()

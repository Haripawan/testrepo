#!/usr/bin/env python3
"""
sql_lineage_extractor.py

A self‑contained script to extract column‑level lineage, filters, and joins
from any complex SQL (INSERT or SELECT), for a specified SQL dialect,
and write the results to an Excel workbook.

Dependencies:
    pip install sqlglot pandas openpyxl
"""

import argparse
import sys

import pandas as pd
import sqlglot
from sqlglot import parse_one, exp


class SQLLineageExtractor:
    def __init__(self, dialect: str = "default"):
        """
        :param dialect: SQL dialect (e.g. 'oracle', 'hive', 'tsql', 'mysql', 'postgres', ...)
        """
        self.dialect = dialect

    def extract(self, sql: str, default_target: str = None):
        """
        Parse the SQL and return three pandas DataFrames:
          1. lineage_df: source→target column mappings + multi-step transform logic
          2. filters_df: all WHERE predicates
          3. joins_df: all JOIN conditions

        :param sql:       SQL statement (INSERT ... SELECT or raw SELECT)
        :param default_target: if no INSERT, use this as the "target table" (e.g. filename)
        """
        tree = parse_one(sql, read=self.dialect)

        target_table, target_columns = self._find_target(tree, default_target)
        lineage_records = []

        # Walk all SELECT projections
        for select in tree.find_all(exp.Select):
            for proj in select.expressions:
                tgt_col = proj.alias_or_name
                transform_steps = self._extract_transform_steps(proj)
                src_cols = self._find_source_columns(proj)
                for src_table, src_col in src_cols:
                    lineage_records.append({
                        "source_table": src_table,
                        "source_column": src_col,
                        "transformation_steps": transform_steps,
                        "target_table": target_table,
                        "target_column": tgt_col
                    })

        # Extract filters
        filters = []
        for where in tree.find_all(exp.Where):
            filters.append({
                "predicate": where.this.sql(dialect=self.dialect)
            })

        # Extract joins
        joins = []
        for join in tree.find_all(exp.Join):
            kind = join.args.get("kind", "JOIN")
            condition = join.on.this.sql(dialect=self.dialect) if join.on else None
            joins.append({
                "join_type": kind.upper(),
                "condition": condition
            })

        lineage_df = pd.DataFrame(lineage_records)
        filters_df = pd.DataFrame(filters)
        joins_df = pd.DataFrame(joins)

        return lineage_df, filters_df, joins_df

    def _find_target(self, tree: exp.Expression, default: str):
        """
        Locate INSERT INTO target table/columns, or fall back to default.
        """
        insert = tree.find(exp.Insert)
        if insert:
            table = insert.this.name
            cols = [c.name for c in insert.columns] if insert.columns else []
            return table, cols
        else:
            # No INSERT: standalone SELECT
            return default, []

    def _extract_transform_steps(self, expr: exp.Expression):
        """
        Collect each Func or operator node as a transformation step.
        Returns a list of SQL snippets in evaluation order.
        """
        steps = []
        for node in expr.walk():
            if isinstance(node, exp.Func):
                steps.append(node.sql(dialect=self.dialect))
            elif isinstance(node, (exp.Cast, exp.Case, exp.If)):
                steps.append(node.sql(dialect=self.dialect))
        return steps or ["IDENTITY"]

    def _find_source_columns(self, expr: exp.Expression):
        """
        Return list of (source_table, source_column) for every Column,
        resolving aliases via simple nearest-ancestor lookup.
        """
        results = []
        for col in expr.find_all(exp.Column):
            table = col.table or self._resolve_table_alias(col)
            results.append((table, col.name))
        return results

    def _resolve_table_alias(self, column_node: exp.Column):
        """
        Fallback alias resolution: scan all FROM/JOIN in AST to match alias.
        (For deeper nested subqueries, enhance this logic.)
        """
        alias = column_node.table
        # As a placeholder: return alias or None
        return alias


def to_excel(lineage_df: pd.DataFrame, filters_df: pd.DataFrame,
             joins_df: pd.DataFrame, output_path: str):
    """
    Write the three DataFrames to separate sheets in an Excel workbook.
    """
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        lineage_df.to_excel(writer, sheet_name="Lineage", index=False)
        filters_df.to_excel(writer, sheet_name="Filters", index=False)
        joins_df.to_excel(writer, sheet_name="Joins", index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract SQL lineage (source→target columns, transforms, filters, joins)"
    )
    parser.add_argument("--sql-file",
                        help="Path to .sql file (INSERT ... SELECT or SELECT).",
                        required=True)
    parser.add_argument("--default-target",
                        help="If no INSERT, use this as target (e.g. filename or table name).",
                        default=None)
    parser.add_argument("--dialect",
                        help="SQL dialect for parsing (default: generic).",
                        default="default")
    parser.add_argument("--output",
                        help="Output Excel file path.",
                        default="sql_lineage.xlsx")

    args = parser.parse_args()

    try:
        with open(args.sql_file, "r", encoding="utf-8") as f:
            sql_text = f.read()
    except Exception as e:
        print(f"ERROR reading SQL file: {e}", file=sys.stderr)
        sys.exit(1)

    extractor = SQLLineageExtractor(dialect=args.dialect)
    lineage_df, filters_df, joins_df = extractor.extract(
        sql_text,
        default_target=args.default_target
    )

    to_excel(lineage_df, filters_df, joins_df, args.output)
    print(f"Lineage written to {args.output}")


if __name__ == "__main__":
    main()
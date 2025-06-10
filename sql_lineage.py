#!/usr/bin/env python3
"""
sql_lineage_extractor.py

A self‑contained script to extract column‑level lineage, filters, and joins
from any complex SQL (INSERT or SELECT), including WITH/CTE support, for a
specified SQL dialect, and write the results to an Excel workbook.

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
        # Will hold CTE definitions: name -> SELECT AST
        self.ctes = {}

    def extract(self, sql: str, default_target: str = None):
        """
        Parse the SQL and return three pandas DataFrames:
          1. lineage_df: source→target column mappings + multi-step transform logic
          2. filters_df: all WHERE predicates
          3. joins_df: all JOIN conditions

        :param sql:       SQL statement (INSERT ... SELECT or raw SELECT, possibly with WITH)
        :param default_target: if no INSERT, use this as the "target table" (e.g. filename)
        """
        # 1. Parse to AST
        tree = parse_one(sql, read=self.dialect)

        # 2. Extract any WITH / CTE definitions
        with_expr = tree.find(exp.With)
        if with_expr:
            # Map each CTE alias -> its SELECT AST
            for cte in with_expr.expressions:
                # cte.alias is an exp.TableAlias; its name is the CTE name
                alias = cte.alias_or_name
                self.ctes[alias] = cte.this  # the SELECT (or other) expression
            # The real query is the 'this' of the WITH node
            tree = with_expr.this
        else:
            self.ctes = {}

        # 3. Determine target table & columns
        target_table, _ = self._find_target(tree, default_target)

        # 4. Walk SELECT projections to build lineage
        lineage_records = []
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

        # 5. Extract filters
        filters = []
        for where in tree.find_all(exp.Where):
            filters.append({
                "predicate": where.this.sql(dialect=self.dialect)
            })

        # 6. Extract joins
        joins = []
        for join in tree.find_all(exp.Join):
            kind = join.args.get("kind", "JOIN")
            condition = None
            if join.on and isinstance(join.on, exp.On):
                condition = join.on.this.sql(dialect=self.dialect)
            joins.append({
                "join_type": kind.upper(),
                "condition": condition
            })

        # 7. Build DataFrames
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
        Collect each Func, Cast, Case, or If node as a transformation step.
        Returns a list of SQL snippets in evaluation order.
        """
        steps = []
        for node in expr.walk():
            if isinstance(node, exp.Func) \
               or isinstance(node, exp.Cast) \
               or isinstance(node, exp.Case) \
               or isinstance(node, exp.If):
                steps.append(node.sql(dialect=self.dialect))
        return steps or ["IDENTITY"]

    def _find_source_columns(self, expr: exp.Expression):
        """
        Return list of (source_table, source_column) for every Column,
        resolving CTEs by recursion and falling back to aliases.
        """
        results = []
        for col in expr.find_all(exp.Column):
            tbl = col.table
            # If the table alias is a CTE, expand it
            if tbl and tbl in self.ctes:
                # Drill into that CTE to find its own source for this column
                expanded = self._extract_from_cte(tbl, col.name)
                results.extend(expanded)
            else:
                # Normal base table or inherited alias
                resolved_tbl = tbl or self._resolve_table_alias(col)
                results.append((resolved_tbl, col.name))
        return results

    def _resolve_table_alias(self, column_node: exp.Column):
        """
        Fallback alias resolution: scan the AST for a FROM or JOIN
        that defines this alias. For simplicity, return the alias itself.
        """
        return column_node.table

    def _extract_from_cte(self, cte_name: str, cte_column: str):
        """
        Given a CTE name and one of its output columns,
        walk that CTE’s SELECT AST to find underlying (table, column).
        """
        cte_select = self.ctes.get(cte_name)
        if not isinstance(cte_select, exp.Select):
            return []

        # Find the projection in the CTE that produced cte_column
        for proj in cte_select.expressions:
            if proj.alias_or_name == cte_column:
                # Reuse the normal logic on this projection node
                return self._find_source_columns(proj)
        return []


def to_excel(lineage_df: pd.DataFrame,
             filters_df: pd.DataFrame,
             joins_df: pd.DataFrame,
             output_path: str):
    """
    Write the three DataFrames to separate sheets in an Excel workbook.
    """
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        lineage_df.to_excel(writer, sheet_name="Lineage", index=False)
        filters_df.to_excel(writer, sheet_name="Filters", index=False)
        joins_df.to_excel(writer, sheet_name="Joins", index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract SQL lineage (source→target columns, transforms, filters, joins), with CTE support"
    )
    parser.add_argument("--sql-file",
                        help="Path to .sql file (INSERT ... SELECT or SELECT, possibly WITH).",
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
    
    
    
    
#!/usr/bin/env python3
"""
column_lineage_with_transforms.py

Extract column-level lineage + transformation logic from any SQL
(using sqllineage + sqlglot), then output to Excel.

Dependencies:
    pip install sqllineage sqlglot pandas openpyxl
"""

import argparse
import sys

import pandas as pd
import sqlglot
from sqlglot import exp, parse_one
from sqllineage.runner import LineageRunner


def extract_transforms(sql: str, dialect: str = "default"):
    """
    Parse the outermost SELECT (or INSERT…SELECT) and build a dict:
       target_column -> transformation_sql

    If the projection is simply `col` or `tbl.col`, we record "IDENTITY".
    """
    tree = parse_one(sql, read=dialect)

    # If it's an INSERT, dive into its SELECT
    select = tree.find(exp.Select)
    if select is None:
        raise ValueError("No SELECT found in SQL")

    transforms = {}
    for proj in select.expressions:
        tgt = proj.alias_or_name
        # If the projection is a direct column ref with no functions/operators:
        if isinstance(proj, exp.Column):
            transforms[tgt] = "IDENTITY"
        else:
            # Otherwise pretty‑print the projection expression
            transforms[tgt] = proj.sql(dialect=dialect)
    return transforms


def extract_column_lineage_with_transforms(
    sql: str,
    default_target: str = None,
    dialect: str = "default"
) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
      source_table, source_column, target_table, target_column, transformation
    """
    # 1) Get raw column lineage pairs
    runner = LineageRunner(sql)
    col_pairs = runner.get_column_lineage()

    # 2) Determine target table (from INSERT) or fallback
    tree = parse_one(sql, read=dialect)
    insert = tree.find(exp.Insert)
    if insert:
        target_table = insert.this.name
    else:
        target_table = default_target

    # 3) Fetch transformation snippets
    transforms = extract_transforms(sql, dialect=dialect)

    # 4) Build rows
    rows = []
    for src_col, tgt_col in col_pairs:
        rows.append({
            "source_table": src_col.table,
            "source_column": src_col.name,
            "target_table": target_table,
            "target_column": tgt_col.name,
            "transformation": transforms.get(tgt_col.name, "IDENTITY")
        })

    return pd.DataFrame(rows)


def to_excel(df: pd.DataFrame, path: str):
    """Write the lineage+transform DataFrame to Excel."""
    df.to_excel(path, index=False)


def main():
    parser = argparse.ArgumentParser(
        description="Extract column-level lineage + transforms using sqllineage + sqlglot"
    )
    parser.add_argument(
        "--sql-file", required=True,
        help="Path to the .sql file (INSERT ... SELECT or SELECT)"
    )
    parser.add_argument(
        "--default-target", default=None,
        help="If no INSERT, use this as the target table name"
    )
    parser.add_argument(
        "--dialect", default="default",
        help="sqlglot dialect (mysql, hive, oracle, tsql, etc.)"
    )
    parser.add_argument(
        "--output", default="column_lineage.xlsx",
        help="Output Excel filename"
    )
    args = parser.parse_args()

    try:
        sql_text = open(args.sql_file, encoding="utf-8").read()
    except Exception as e:
        print(f"ERROR reading SQL file: {e}", file=sys.stderr)
        sys.exit(1)

    df = extract_column_lineage_with_transforms(
        sql=sql_text,
        default_target=args.default_target,
        dialect=args.dialect
    )

    to_excel(df, args.output)
    print(f"✅ Written column‑level lineage + transforms to {args.output}")


if __name__ == "__main__":
    main()
SELECT
  '[ ' || RTRIM(XMLCAST(XMLAGG(
    XMLELEMENT(e, CASE WHEN type = 'A' THEN json_data || ', ' END)
    ORDER BY id
  ) AS CLOB), ', ') || ' ]' AS type_a_clob,

  '[ ' || RTRIM(XMLCAST(XMLAGG(
    XMLELEMENT(e, CASE WHEN type = 'B' THEN json_data || ', ' END)
    ORDER BY id
  ) AS CLOB), ', ') || ' ]' AS type_b_clob,

  '[ ' || RTRIM(XMLCAST(XMLAGG(
    XMLELEMENT(e, CASE WHEN type = 'C' THEN json_data || ', ' END)
    ORDER BY id
  ) AS CLOB), ', ') || ' ]' AS type_c_clob

FROM your_table;
SELECT JSON_SERIALIZE(
         JSON_OBJECT(
           'name' VALUE name_column,
           'description' VALUE long_text_column,
           'details' VALUE another_column
         RETURNING CLOB)
       RETURNING CLOB)
FROM your_table;
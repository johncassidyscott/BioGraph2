-- Export MeSH Disease (C) tree to CSV

\copy (
  SELECT
    d.mesh_id,
    d.preferred_name,
    t.tree_number,
    t.parent_tree_number,
    t.tree_level
  FROM mesh_tree_c t
  JOIN mesh_descriptor d ON d.mesh_id = t.mesh_id
  ORDER BY t.tree_number
) TO 'mesh_c_tree_export.csv' WITH CSV HEADER;

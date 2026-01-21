-- Migration for MeSH Disease (C) tree reference tables

CREATE TABLE IF NOT EXISTS mesh_descriptor (
  mesh_id TEXT PRIMARY KEY,
  preferred_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mesh_tree_c (
  mesh_id TEXT NOT NULL REFERENCES mesh_descriptor(mesh_id),
  tree_number TEXT NOT NULL,
  parent_tree_number TEXT NULL,
  tree_level INT NOT NULL,
  PRIMARY KEY(mesh_id, tree_number)
);

CREATE INDEX IF NOT EXISTS idx_mesh_tree_c_tree ON mesh_tree_c(tree_number);
CREATE INDEX IF NOT EXISTS idx_mesh_tree_c_parent ON mesh_tree_c(parent_tree_number);

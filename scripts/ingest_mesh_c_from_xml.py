import os
import gzip
import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import execute_batch

DB_CONN = os.environ.get("DATABASE_URL") or "postgresql://neondb_owner:npg_meyxk4t0dwXI@ep-spring-art-aheyxuga-pooler.c-3.us-east-1.aws.neon.tech/BioGraph?sslmode=require&channel_binding=require"
MESH_URL = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2026.gz"
BATCH_SIZE = 2000


def download_mesh_gz(path="desc2026.gz"):
    import requests
    if not os.path.exists(path):
        print(f"Downloading {MESH_URL}...")
        r = requests.get(MESH_URL, stream=True)
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return path

def is_gzipped(filepath):
    with open(filepath, 'rb') as f:
        return f.read(2) == b'\x1f\x8b'

def parse_and_ingest_mesh_c(xml_gz_path):
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    print("Truncating mesh tables...")
    cur.execute("TRUNCATE mesh_tree_c, mesh_descriptor CASCADE;")
    conn.commit()

    desc_batch = []
    tree_batch = []
    count = 0

    # Detect file type and open appropriately
    if xml_gz_path.endswith('.gz') and is_gzipped(xml_gz_path):
        f = gzip.open(xml_gz_path, "rb")
    else:
        # If not gzipped, treat as plain XML
        if xml_gz_path.endswith('.gz'):
            # Try to find the XML file
            xml_path = xml_gz_path[:-3] + 'xml'
            if not os.path.exists(xml_path):
                print(f"desc2026.gz is not a valid gzip file. Downloading XML fallback...")
                import requests
                xml_url = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/desc2026.xml"
                r = requests.get(xml_url, stream=True)
                r.raise_for_status()
                with open(xml_path, "wb") as xf:
                    for chunk in r.iter_content(chunk_size=8192):
                        xf.write(chunk)
            f = open(xml_path, "rb")
        else:
            f = open(xml_gz_path, "rb")

    context = ET.iterparse(f, events=("end",))
    for event, elem in context:
        if elem.tag == "DescriptorRecord":
            mesh_id = elem.findtext("DescriptorUI")
            preferred_name = elem.findtext("DescriptorName/String")
            tree_numbers = [tn.text for tn in elem.findall("TreeNumberList/TreeNumber") if tn.text and tn.text.startswith("C")]
            if not tree_numbers:
                elem.clear()
                continue
            desc_batch.append((mesh_id, preferred_name))
            for tree_number in tree_numbers:
                parent_tree_number = tree_number.rsplit(".", 1)[0] if "." in tree_number else None
                tree_level = tree_number.count(".") + 1
                tree_batch.append((mesh_id, tree_number, parent_tree_number, tree_level))
            count += 1
            if count % BATCH_SIZE == 0:
                execute_batch(cur, "INSERT INTO mesh_descriptor (mesh_id, preferred_name) VALUES (%s, %s) ON CONFLICT (mesh_id) DO UPDATE SET preferred_name=EXCLUDED.preferred_name", desc_batch)
                execute_batch(cur, "INSERT INTO mesh_tree_c (mesh_id, tree_number, parent_tree_number, tree_level) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", tree_batch)
                conn.commit()
                desc_batch.clear()
                tree_batch.clear()
            elem.clear()
    # Final flush
    if desc_batch:
        execute_batch(cur, "INSERT INTO mesh_descriptor (mesh_id, preferred_name) VALUES (%s, %s) ON CONFLICT (mesh_id) DO UPDATE SET preferred_name=EXCLUDED.preferred_name", desc_batch)
    if tree_batch:
        execute_batch(cur, "INSERT INTO mesh_tree_c (mesh_id, tree_number, parent_tree_number, tree_level) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", tree_batch)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Ingested {count} MeSH C descriptors.")

if __name__ == "__main__":
    gz_path = download_mesh_gz()
    parse_and_ingest_mesh_c(gz_path)

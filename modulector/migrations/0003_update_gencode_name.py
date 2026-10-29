import os
import pathlib
import gzip
import shutil
from django.db import migrations
from tqdm import tqdm

PARENT_DIR = pathlib.Path(__file__).parent.absolute().parent
GTF_PATH = os.path.join(PARENT_DIR, "files/gencode.v41.annotation.gtf")
GTF_GZ_PATH = os.path.join(PARENT_DIR, "files/gencode.v41.annotation.gtf.gz")
TSV_PATH = os.path.join(PARENT_DIR, "files/mapeo_enst_ensg.tsv")

def generate_lightweight_dictionary(gtf_input: str, tsv_output: str):
    """
    Parses a GENCODE GTF file and extracts the mapping between transcript IDs (ENST) 
    and gene IDs (ENSG) into a lightweight TSV format.
    
    Args:
        gtf_input (str): Path to the input GENCODE GTF file.
        tsv_output (str): Path where the lightweight TSV mapping will be saved.
    """
    with open(gtf_input, 'r') as f_in, open(tsv_output, 'w') as f_out:
        # Write the header of the new file
        f_out.write("ENST\tENSG\n")
        
        for line in f_in:
            # Skip headers/comments
            if line.startswith('#'): 
                continue
            
            columns = line.split('\t')
            
            # Process only if the feature type is a transcript
            if columns[2] == 'transcript':
                attributes = columns[8]
                
                # Extract gene_id and transcript_id by splitting the attributes text
                gene_id = [x for x in attributes.split(';') if 'gene_id' in x][0].split('"')[1]
                transcript_id = [x for x in attributes.split(';') if 'transcript_id' in x][0].split('"')[1]
                
                # Save to the new lightweight file
                f_out.write(f"{transcript_id}\t{gene_id}\n")

def check_and_generate_files(apps, schema_editor):
    """
    Checks if the TSV dictionary exists; if not, generates it from the GTF file.
    Raises a FileNotFoundError if the required GTF file is missing.
    """
    if not os.path.exists(TSV_PATH):
        if not os.path.exists(GTF_PATH):
            if os.path.exists(GTF_GZ_PATH):
                print(f"\n--- Decompressing {GTF_GZ_PATH} ---")
                with gzip.open(GTF_GZ_PATH, 'rb') as f_in:
                    with open(GTF_PATH, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                raise FileNotFoundError(
                    "Missing required data file: gencode.v41.annotation.gtf.gz. "
                    "Please download it following the instructions in DEPLOYING.md "
                    "and place it in modulector/files/."
                )
        print("\n--- Generating lightweight ENST to ENSG dictionary ---")
        generate_lightweight_dictionary(GTF_PATH, TSV_PATH)

def update_gencode_names(apps, schema_editor):
    """
    Updates the gencode_name field of MethylationGencode records based on the TSV mapping.
    Records that already start with 'ENSG' are skipped.
    """
    MethylationGencode = apps.get_model('modulector', 'MethylationGencode')
    
    # Load TSV mapping into memory
    print("\n--- Loading ENST to ENSG mapping into memory ---")
    mapping = {}
    with open(TSV_PATH, 'r') as f:
        # Skip header
        next(f, None)
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                mapping[parts[0]] = parts[1]
                
    # Fetch records where gencode_name does not start with "ENSG"
    print("\n--- Updating MethylationGencode records ---")
    
    records_to_update = MethylationGencode.objects.exclude(gencode_name__startswith='ENSG')
    
    updates = []
    batch_size = 5000
    
    total_records = records_to_update.count()
    if total_records == 0:
        print("No records need updating.")
        return

    # Using tqdm for progress bar
    iterator = tqdm(records_to_update.iterator(), total=total_records, desc="Updating records")

    updated_count = 0
    for record in iterator:
        enst = record.gencode_accession
        if enst in mapping:
            record.gencode_name = mapping[enst]
            updates.append(record)
            updated_count += 1
            
        if len(updates) >= batch_size:
            MethylationGencode.objects.bulk_update(updates, ['gencode_name'])
            updates.clear()
            
    if updates:
        MethylationGencode.objects.bulk_update(updates, ['gencode_name'])
        
    print(f"\nUpdated {updated_count} records.")
    
    # Clean up the lightweight dictionary file
    if os.path.exists(TSV_PATH):
        os.remove(TSV_PATH)
        print(f"--- Deleted temporary file {TSV_PATH} ---")

class Migration(migrations.Migration):

    dependencies = [
        ('modulector', '0002_load_data'),
    ]

    operations = [
        migrations.RunPython(
            code=check_and_generate_files,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            code=update_gencode_names,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

# Data sources and terms

This file records the provenance and use conditions for data used with
Modulector. It is not legal advice. Review the current source terms and obtain
any required permission before loading, serving, or redistributing a dataset.

## Scope of the MIT license

The repository [MIT License](LICENSE) applies only to Modulector's source code
and project-authored documentation. It does **not** grant rights to any
third-party dataset, database, record, annotation, or data-derived database
created by running Modulector. Each upstream source remains subject to its own
terms.

## Data included in this repository

| Files | Source and terms | Required notice |
| --- | --- | --- |
| `modulector/files/mature.fa`, `hairpin.fa`, `miraccs*.csv`, `miraccs-adapted.*`, and `mirna_mature.txt` | Derived from [miRBase](https://mirbase.org/), which states that its database is in the public domain and may be modified, redistributed, and used for any purpose. | Cite miRBase as requested by its [licence notice](https://mirbase.org/download/CURRENT/LICENSE/). |
| `modulector/files/ref_seq_to_symbols.txt` and `ref_seq_translation.sql` | Derived from NCBI RefSeq/Gene mappings. NCBI places no restriction on use or distribution of molecular data, but does not transfer any rights that an original submitter might claim. | Acknowledge NCBI and preserve the [NCBI data-usage notice](https://www.ncbi.nlm.nih.gov/home/about/policies/). |

The table identifies provenance; it does not relicense those files under MIT.

## Data not distributed with Modulector

The following source datasets must not be added to this repository, a public
container image, release asset, or public database dump unless the maintainer
has a written permission that covers the intended distribution and service.
Keep any permitted local copy outside version control.

The Docker build context explicitly excludes the filenames listed below, so a
local copy cannot be included in a Modulector image by accident.

| Source | Reason and deployment rule |
| --- | --- |
| [SM2miR](https://doi.org/10.1093/bioinformatics/bts698) | No explicit redistribution licence was located for the SM2miR data used by the project. `drugs.xls` was removed from the repository. Do not restore it or expose the data through a service without written permission from the rights holder. |
| [HMDD v4.0](https://www.cuilab.cn/hmdd) | HMDD states that its data are free only for academic use and asks commercial users to contact the authors. `disease_hmdd.txt` was removed. Cite Cui et al., *Nucleic Acids Research* 2024, doi:10.1093/nar/gkad717, when use is authorised. |
| [mirDIP](https://ophid.utoronto.ca/mirDIP/download.jsp) | Its terms allow use, copying, and modification without fee for academic and not-for-profit institutions; distribution or extended versions are explicitly limited to non-profit organisations, with the organisation and authors named in copies. Commercial users must contact the authors. |
| [miRTarBase](https://mirtarbase.cuhk.edu.cn/) | The legacy `pubmed_file.xlsx` was a miRTarBase export and was removed. The published miRTarBase licence is for academic/non-profit use with attribution; confirm the current download terms before use. |
| [Illumina Infinium MethylationEPIC v2.0 product files](https://support.illumina.com/downloads/infinium-methylationepic-v2-0-product-files.html) | The product files are copyrighted Illumina materials and are supplied for research use. Obtain them directly from Illumina and follow the terms that accompany the download; do not bundle `EPIC.csv`. |

These restrictions also apply to derived copies that reproduce a substantial
part of an upstream dataset. In particular, an MIT-licensed codebase cannot
turn academic-only, non-commercial, proprietary, or unlicensed data into
unrestricted data.

## Local data provisioning

Some migrations can load optional external files from `modulector/files/`.
They now skip the import when the file is absent, so a clean source checkout
does not distribute or require restricted data. Consult
[DEPLOYING.md](DEPLOYING.md) and the source's own current terms before placing
a file there.

Before publishing an API, container image, database dump, or derived dataset,
confirm that every loaded source authorises that form of use and distribution.
For commercial or public hosted deployments, obtain written permission where
the upstream terms do not expressly allow it.

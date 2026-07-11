# Local source data

This directory contains the miRBase and NCBI-derived files distributed with
the source tree. Their provenance and notices are listed in
[DATA-LICENSES.md](../../DATA-LICENSES.md); they are not relicensed under MIT.

Do not commit third-party downloads here. In particular, the following files
are intentionally not distributed: `drugs.xls` (SM2miR), `disease_hmdd.txt`
(HMDD), `mirDIP_Unidirectional_search.txt`, `EPIC.csv`, `hsa_MTI.csv`, and the
legacy miRTarBase spreadsheet. A migration skips an optional import when its
source file is absent.

Obtain any permitted external data directly from its provider, retain the
provider's notices, and use it only under terms that cover your organisation,
deployment, and distribution model.

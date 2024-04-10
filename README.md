# Modulector

Modulector is a performing open platform that provides information about miRNAs, genes and methylation sites based on a compilation of information from different resources.

Document content:

- [Modulector](#modulector)
  - [Integrated databases](#integrated-databases)
  - [Usage](#usage)
    - [General](#general)
    - [Sorting](#sorting)
    - [Filters](#filters)
    - [Search](#search)
    - [Pagination](#pagination)
    - [Combining functions](#combining-functions)
  - [Services](#services)
    - [MiRNA target interactions](#mirna-target-interactions)
    - [MiRNA details](#mirna-details)
    - [MiRNA aliases](#mirna-aliases)
    - [MiRNA codes finder](#mirna-codes-finder)
    - [miRNA codes](#mirna-codes)
    - [Methylation sites finder](#methylation-sites-finder)
    - [Methylation sites](#methylation-sites)
    - [Genes of methylation sites](#genes-of-methylation-sites)
    - [Methylation site details](#methylation-site-details)
    - [Diseases](#diseases)
    - [Drugs](#drugs)
    - [Subscribe to PUBMEDS news](#subscribe-to-pubmeds-news)
    - [Unsubscribe from PUBMEDS news](#unsubscribe-from-pubmeds-news)
  - [Considerations](#considerations)
  - [Contributing](#contributing)
  - [Sonarcloud](#sonarcloud)
  - [License](#license)

## Integrated databases

Modulector obtains information from different bioinformatics databases or resources. These databases were installed locally to reduce data search time. The databases currently integrated to Modulector are:

1. miRNA data: [mirDIP: microRNA Data Integration Portal](https://ophid.utoronto.ca/mirDIP/).  
   mirDIP is an integrative database of human microRNA target predictions. Modulector use mirDIP 5.2.  
2. miRNA data: [miRBase: the microRNA database](https://mirbase.org/).  
   miRBase is a searchable database of published miRNA sequences and annotations. Each entry in the miRBase Sequence database represents a predicted hairpin portion of a miRNA transcript (termed hairpin in the database), with information on the location and sequence of the mature miRNA sequence (termed mature). Modulector use miRBase 22.1.  
3. Relationship data between miRNA and diseases: [HMDD: the Human microRNA Disease Database](https://www.cuilab.cn/hmdd).  
   Increasing reports have shown that miRNAs play important roles in various critical biological processes. For their importance, the dysfunctions of miRNAs are associated with a broad spectrum of diseases. The Human microRNA Disease Database (HMDD) is a database that curated experiment-supported evidence for human microRNA (miRNA) and disease associations. Modulector use HMDD v4.0.
4. Relationship data between miRNA and drugs: [SM2miR Database](http://www.jianglab.cn/SM2miR/).
   Many studies have demonstrated that bioactive small molecules (or drugs) can regulate the miRNA expression, which indicate that targeting miRNAs with small molecules is a new type of therapy for human diseases. SM2miR is a manual curated database which collects and incorporates the experimentally validated small molecules' effects on miRNA expression in 21 species from the published papers. Modulector uses leaked data from the SM2miR database for Homo Sapiens, in the version released on Apr. 27, 2015.
5. Methylation data: Illumina [Infinium MethylationEPIC 2.0](https://www.illumina.com/products/by-type/microarray-kits/infinium-methylation-epic.html) array.  
   The Infinium MethylationEPIC v2.0 BeadChip Kit is a genome-wide methylation screening tool that targets over 935,000 CpG sites in the most biologically significant regions of the human methylome. At Modulector we use the information provided by Illumina on its [product files](https://support.illumina.com/downloads/infinium-methylationepic-v2-0-product-files.html) website.  

## Usage

Modulector can be used through the graphical interfaces provided in [Multiomix][multiomix-site], or it can be hosted on your server (read [DEPLOYING.md](DEPLOYING.md) for more information). We strongly recommend using this software through the Multiomix application.

All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format. In addition to the information provided, sorting, filtering, searching, and paging functions are also available. How to use these functions is explained below:

### General

All functions are used as a parameter in the URL. So if you want to access `https://modulector.multiomix.org/service/` by sending parameters to it, just add the following suffix to the end of the URL: `?parameter1=value&parameter2=value&parameter3=value`. The `?` indicates that the parameter section begins, these will be of the form `parameterName=parameterValue` and are separated, in case you need to send more than one, by a `&`.

### Sorting

To sort you must specify the parameter `ordering=fieldToSort`, if you want to sort descending you must add a `-` before the field name. You can specify several fields to sort separated by *commas*.

For example, if you want to consume the [miRNA-target interactions](#mirna-target-interactions) service by sorting by `score` descending and by `gene` ascending you can access the URL:

`https://modulector.multiomix.org/mirna-target-interactions/?ordering=-score,gene`

### Filters

To filter it is enough to specify the field and the value by which you want to filter. For example, if you want to consume the [miRNA aliases](#mirna-aliases) service keeping only the aliases of `MIMAT0000062` you could access the following resource:

`https://modulector.multiomix.org/mirna-aliases/?mirbase_accession_id=MIMAT0000062`

### Search

The search is done on the basis of a single parameter called `search` which must contain the value to be searched for. Unlike the filter, the search can be performed on multiple fields at once and is performed by *containing* the search term in the field and is case insensitive (while the filter is by exact value). The fields considered in the search are fixed and will be specified for each service later. For example, the [drugs](#drugs) service allows a search by the `condition`, `small_molecule`, and `expression_pattern` fields, then the following query could be performed:

`https://modulector.multiomix.org/drugs/?mirna=miR-126*search=breast`

### Pagination

Some services can return so many items that paginated responses were chosen so that they are efficient queries of few items and can be traversed through parameterizable pages. There are two parameters that can be specified to handle pagination:

- `page`: allows you to specify the current page. If not specified, the default value `1` is used.
- `page_size`: number of elements to return per page. If not specified, the default value `10` is used. The value cannot   be greater than `1000`.

All the paginated responses contain the following fields:

- `count`: total number of elements in Modulector database. This field is useful to compute number of pages (which is   equal to `ceil(count / page_size)`).
- `next`: link to the next page.
- `previous`: link to the previous page.
- `results`: array of elements (the structure of each element depends on the service and is explained in detail in the [services](#services) section).

### Combining functions

All of the above parameters can be used together! For example, if we wanted to consume the [diseases](#diseases) service by sorting ascending by disease, performing a disease search and keeping only the first 3 items, we could perform the following query (the order of the parameters **does not matter**):

`https://modulector.multiomix.org/diseases/?ordering=disease&search=leukemia&page_size=3`

**It will be indicated for each service which fields are available for filtering, sorting, and/or searching**.

## Services

### MiRNA target interactions

Receives a miRNA and/or a gene symbol and returns a paginated vector. Each vector entry represents a miRNA-Gene interaction.  
If no gene symbol is entered, all miRNA interactions are returned. If a miRNA is not entered, all gene interactions are returned. If both are entered, the interaction of mirna with the gene is returned.

- URL: `/mirna-target-interactions`
- Query params:
  - `mirna`: miRNA (Accession ID or name in mirBase) to get its interactions with different genes targets.
  - `gene`: gene symbol to get its interactions with different miRNA targets.
  - `score`: numerical score to filter the interactions (only interactions with a score greater than or equal to the parameter value are returned). The score corresponds to that obtained for the unidirectional analysis of the MirDip tool. MiRDIP groups information from [24 different predictors](https://ophid.utoronto.ca/mirDIP/statistics.jsp) to then calculate a score for each target gene. For more information about the calculation of the score, you can consult the [scientific publication](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9825511/) of the tool.  
  - `include_pubmeds`: if its value is 'true', the endpoint also returns a list of links to Pubmed where the miRNAs are related to the genes (this may affect Modulector's response time). The default is 'false'.
*NOTE*: `mirna` or `gene` are required
- Functions:
  - Ordering fields: `gene` and `score`
  - Filtering fields: filtering is not available for this service
  - Searching fields: `gene`
  - Pagination: yes
- Success Response:
  - Code: 200
  - Content:
    - `id`: Record identifier in MirDIP.
    - `mirna`: miRNA ID (miRBase MIMAT id or previous ID). The received one as query param.
    - `gene`: target gene.
    - `score`: interaction score (according to mirDIP). Value range between 0 and 1.
    - `source_name`: database from which the interaction was extracted. For now you will always receive the `mirdip` value.  
    - `pubmeds`: array of PubMed URLs for the miRNA-gene interaction (according to mirTaRBase).
    - `sources`: miRNA-Gene interaction sources. mirDIP score is based on the scores of those sources. This field is an array that contains the interaction score source names. The different source databases can be found on the [official miRDIP site](https://ophid.utoronto.ca/mirDIP/statistics.jsp).
    - `score_class`: score class according to mirDIP. The possible values are: `V` (Very high: Top 1%), `H` (High: Top 5%), `M` (Medium: Top 1/3) or `L` (Low: Bottom 2/3).
  - Example:
    - URL: <http://localhost:8000/mirna-target-interactions/?mirna=hsa-miR-891a-5p&gene=EGFR&include_pubmeds=true>
    - Response:

    ```JSON
      {
        "count":1,
        "next":null,
        "previous":null,
        "results":[
            {
                "id":629118277,
                "mirna":"hsa-miR-891a-5p",
                "gene":"EGFR",
                "score":0.0684,
                "source_name":"mirdip",
                "pubmeds":[
                    "https://pubmed.ncbi.nlm.nih.gov/5362487",
                    "https://pubmed.ncbi.nlm.nih.gov/10120249",
                    "https://pubmed.ncbi.nlm.nih.gov/8948606",
                    "https://pubmed.ncbi.nlm.nih.gov/5642539",
                    "https://pubmed.ncbi.nlm.nih.gov/9361765",
                    "https://pubmed.ncbi.nlm.nih.gov/4895700"
                ],
                "sources":[
                    "MirAncesTar",
                    "mirmap_May_2021",
                    "MiRNATIP"
                ],
                "score_class":"M"
            }
        ]
      }
    ```  

- Error Response:
  - Code: 400
  - Content: `detail`: error description

### MiRNA details

This functionality allows obtaining different information about a miRNA, such as its sequence, its previous identifiers and databases where information about it can be found.

- URL: `/mirna`
- Required query params:
  - `mirna`: miRNA identifier (miRNA code or Accession ID)
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content:
    - `aliases`: array of miRNA aliases (previous IDs according to miRBase).
    - `mirna_sequence`: miRNA nucleotide sequence.
    - `mirbase_accession_id`: miRNA accession ID (MIMAT) according to miRBase DB.
    - `links`: List of JSON containing the following information:
      - `source`: Name of the database where you can find information related to miRNA. For this version you will always receive the `mirbase` value.
      - `url`: URL to access the source database for the miRNA of interest.
  - Example:
    - URL: <http://localhost:8000/mirna/?mirna=hsa-miR-548ai>
    - Response:

      ```JSON
        {
          "aliases":[
              "hsa-miR-548ai",
              "MIMAT0018989",
              "hsa-miR-548ai"
          ],
          "mirna_sequence":"AAAGGUAAUUGCAGUUUUUCCC",
          "mirbase_accession_id":"MIMAT0018989",
          "links":[
              {
                  "source":"mirbase",
                  "url":"http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=MIMAT0018989"
              }
          ]
        }
      ```  

- Error Response:
  - Code: 404
  - Content: `detail`: error description

### MiRNA aliases

Returns all associations between mirnas Accessions IDs (MIMAT) and miRNAs matures IDs from the miRBase database.  
The main difference between MIMAT and mature miRNA IDs in MiRBase lies in their purpose and usage. MIMAT are unique identifiers that define miRNAs uniquely in MiRBase, allowing users to retrieve comprehensive information about specific miRNAs, including their names, sequences, species, versions, and families. On the other hand, mature miRNA IDs refer to the specific mature sequences of miRNAs, such as miR-17-5p and miR-17-3p, which are excised from hairpin precursors and represent different arms of the miRNA. While accession IDs serve as universal identifiers for miRNAs across different versions of MiRBase, mature miRNA IDs focus on the individual sequences of mature miRNAs and their relationships within the database.

- URL: `/mirna-aliases`
- Required query params: -
- Functions:
  - Ordering fields: `mature_mirna`
  - Filtering fields: `mature_mirna` and `mirbase_accession_id`
  - Searching fields: searching is not available for this service
  - Pagination: yes
- Success Response:
  - Code: 200
  - Content:
    - `mirbase_accession_id`: mirBase accession ID (MIMAT) for the miRNA.
    - `mature_mirna`: Mature mirna ID in miRBase database.
  - Example:
    - URL: <http://localhost:8000/mirna-aliases/?mirbase_accession_id=MIMAT0000062>
    - Response:

      ```JSON
        {
          "count":1,
          "next":null,
          "previous":null,
          "results":[
              {
                  "mirbase_accession_id":"MIMAT0000062",
                  "mature_mirna":"hsa-let-7a-5p"
              }
          ]
        }
      ```  

- Error Response: -

### MiRNA codes finder

Service that takes a string of any length and returns a list of miRNAs that contain that search criteria.

- URL: `/mirna-codes-finder`
- Method: GET
- Required query params:
  - `query`: mirna search string.  
- Optional query params:
  - `limit`: number of elements returned by the service. `50` by default and a maximum of `3000`.
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content: a list of miRNAs (IDs or accession IDs from miRbase DB) matching the search criteria.
  - Example:
    - URL: <http://localhost:8000/mirna-codes-finder/?query=hsa-let-7a>
    - Response:

      ```JSON
        [
          "hsa-let-7a-3",
          "hsa-let-7a-2",
          "hsa-let-7a-3p",
          "hsa-let-7a-2-3p",
          "hsa-let-7a-1",
          "hsa-let-7a-5p"
        ]
      ```  

- Error Response: -

### miRNA codes

Searches for codes from a list of miRNA identifiers and returns the approved access identifier according to miRBase DB (MI or MIMAT ID).

- URL: `/mirna-codes`
- Method: POST
- Required body params (in JSON format):  
  - `mirna_codes`: list of identifiers that you want to get your accession ID from miRBase DB.  
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content:
    - `mirna_codes`: a JSON object with as many keys as miRNAs in the body of the request. For each miRNA, the value is a valid miRNA accession ID or `null`.  
  - Example:
    - URL: <http://localhost:8000/mirna-codes/>
    - body:

      ```JSON
        {
          "mirna_codes":[
              "name_01",
              "Hsa-Mir-935-v2_5p*",
              "MIMAT0000066",
              "MI0026417",
              "hsa-let-7e-5p"
          ]
        }
      ```

    - Response:

      ```JSON
        {
          "name_01":null,
          "Hsa-Mir-935-v2_5p*":null,
          "MIMAT0000066":"MIMAT0000066",
          "MI0026417":"MI0026417",
          "hsa-let-7e-5p":"MIMAT0000066"
        }
      ```  

- Error Response:
  - Code: 400
  - Content:
    - `detail`: a text with information about the error.  

### Methylation sites finder

Service that takes a text string of any length and returns a list of methylation sites names (loci) containing that search criteria within the Illumina *Infinium MethylationEPIC 2.0* array.

- URL: `/methylation-sites-finder`
- Method: GET
- Required query params:
  - `query`: Methylation search string.  
- Optional query params:
  - `limit`: number of elements returned by the service. `50` by default and a maximum of `3000`.
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content: a list of methylation sites from the Illumina 'Infinium MethylationEPIC 2.0' array matching the search criteria.
  - Example:
    - URL: <http://localhost:8000/methylation-sites-finder/?query=cg25&limit=5>
    - Response:

      ```JSON
        [
          "cg25324105",
          "cg25383568",
          "cg25455143",
          "cg25459778",
          "cg25487775"
        ]
      ```  

- Error Response: -

### Methylation sites

Searches a list of methylation site names or IDs from different Illumina array versions and returns the name for the *Infinium MethylationEPIC 2.0* array.

- URL: `/methylation-sites`
- Method: POST
- Required body params (in JSON format):
  - `methylation_sites`: list of names or identifiers that you want to get your current name from Illumina 'Infinium MethylationEPIC 2.0' array.  
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content:
    - `methylation_sites`: a JSON object with as many keys as methylation names in the body of the request. For each methylation name, the value is a list of valid methylation names to Illumina *Infinium MethylationEPIC 2.0* array.
  - Example:
    - URL: <http://localhost:8000/methylation-sites/>
    - body:

      ```JSON
        {
          "methylation_sites":[
              "cg17771854_BC11",
              "cg01615704_TC11"
          ]
        }
      ```

    - Response:

      ```JSON
        {
          "cg17771854_BC11":[
              "cg17771854"
          ],
          "cg01615704_TC11":[
              "cg01615704"
          ]
        }
      ```  

- Error Response:
  - Code: 400
  - Content:
    - `detail`: a text with information about the error.  

### Genes of methylation sites

A service that searches from a list of CpG methylation site identifiers from different versions of Illumina arrays and returns the gene(s) to which they belong.  

- URL: `/methylation-sites-genes`
- Method: POST
- Required body params (in JSON format):
  - `methylation_sites`: list of Illumina array methylation site names or identifiers for which you want to know the gene(s).  
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content:
    - Returns a JSON with as many keys as there are methylation names/ids in the body. For each methylation name/ID, the value is a list of genes that the name/ID methylates.  
  - Example:
    - URL: <http://localhost:8000/methylation-sites-genes/>
    - body:

      ```JSON
        {
          "methylation_sites":[
              "cg17771854_BC11",
              "cg22461615_TC11",
              "name_007"
          ]
        }
      ```

    - Response:

      ```JSON
        {
          "cg17771854_BC11":[
              "IPO13"
          ],
          "cg22461615_TC11":[
              "THAP9",
              "THAP9-AS1",
              "SEC31A"
          ]
        }
      ```  

- Error Response:
  - Code: 400
  - Content:
    - `detail`: a text with information about the error.  

### Methylation site details

Returns information on a methylation site.

- URL: `/methylation`
- Required query params:
  - `methylation_site`: methylation_site name from Illumina *Infinium MethylationEPIC 2.0* array
- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no
- Success Response:
  - Code: 200
  - Content:
    - `name`: name of methylation site according to the Illumina Infinium MethylationEPIC 2.0 array.
    - `aliases`: list of other names for the same methylation site on other Illumina arrays (EPIC v2, EPIC v1, Methyl450, and Methyl27).
    - `chromosome_position`: String with information about the chromosome, position, and strand on which the site is located. Format: `chr:position [strand]`
    - `ucsc_cpg_islands`: List of islands related to the methylation site according to the UCSC database. Each element in the view is a JSON with the following content:  
      - `cpg_island`: chromosomal coordinates where the island is located. Format: `chr:start position-end position`
      - `relation`: Relation of the site to the CpG island. The values it can take are `Island`=within boundaries of a CpG Island, `N_Shore`=0-2kb 5' of Island, `N_Shelf`=2kb-4kb 5' of Island, `S_Shore`=0-2kb 3' of Island, `S_Shelf`=2kb-4kb 3' of Island.
    - `genes`: The value is a JSON where each key is a gene that is related to the methylation site. Values for each gene is a list that contains the region of the gene where the methylation site is located. These regions, according to the NCBI RefSeq database, can be: `5UTR`=5' untranslated region between the TSS and ATG start site, `3UTR`=3' untranslated region between stop codon and poly A signal, `exon_#`, `TSS200`=1-200 bp 5' the TSS, or `TS1500`=200-1500 bp 5' of the TSS. TSS=*Transcription Start Site*.
  - Example:
    - URL: <http://localhost:8000/methylation/?methylation_site=cg22461615>
    - Response:

      ```JSON
        {
          "name":"cg22461615",
          "chromosome_position":"chr4:82900764 [+]",
          "aliases":[
              "cg22461615_TC11"
          ],
          "ucsc_cpg_islands":[
              {
                  "cpg_island":"chr4:82900535-82900912",
                  "relation":"Island"
              }
          ],
          "genes":{
              "THAP9":[
                  "5UTR",
                  "exon_1"
              ],
              "THAP9-AS1":[
                  "exon_1"
              ],
              "SEC31A":[
                  "TSS200"
              ]
          }
        }
      ```  

    *NOTE*: Multiple values of the same gene name indicate splice variants.  
- Error Response:
  - Code: 400
  - Content: error explanation text  

### Diseases

This service provides information, with evidence supported by experiments, on the relationships between miRNAs and human diseases.

- URL: `/diseases`
- Method: GET
- Required query params:
  - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.
- Functions:
  - Ordering fields: `disease`
  - Filtering fields: filtering is not available for this service
  - Searching fields: `disease`
  - Pagination: yes
- Success Response:
  - Code: 200
  - Content:
    - `id`: Internal ID of the record in the HMDD database.
    - `category`: Category codes assigned by the HMDD database to classify diseases. Possible codes can be found in the [database documentation](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10767894/table/tbl1/?report=objectonly).
    - `disease`: Name of the disease associated with the miRNA used as a parameter.
    - `pubmed`: URL to the scientific article in the Pubmed database where the evidence that relates miRNA to the disease is found.
    - `description`: Short description of why this miRNA is related to this disease.
  - Example:
    - URL: <http://localhost:8000/diseases/?mirna=hsa-miR-9500>
    - Response:

      ```JSON
        {
          "count":1,
          "next":null,
          "previous":null,
          "results":[
              {
                  "id":3540992,
                  "category":"target gene",
                  "disease":"Liver Neoplasms",
                  "pubmed":"https://pubmed.ncbi.nlm.nih.gov/24658401",
                  "description":"The novel miR-9500 regulates the proliferation and migration of human lung cancer cells by targeting Akt1."
              }
          ]
        }
      ```  

- Error Response:
  - Code: 200
  - Content: empty paginated response (number of elements = 0)
- Additional details: **We capitalize the R present in the miRNA for each record in HMDD database because they are mature, however, the file does not format it correctly and on the website they show up capitalized**

### Drugs

Returns a paginated response of experimentally validated small molecules (or drugs) that affect miRNA expression.

- URL: `/drugs`
- Method: GET
- Required query params:
  - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.
- Functions:
  - Ordering fields: `condition`, `detection_method`, `small_molecule`, `expression_pattern`, `reference`
      and `support`
  - Filtering fields: `fda_approved` (possible values: `true` or `false`)
  - Searching fields: `condition`, `small_molecule`, and `expression_pattern`
  - Pagination: yes
- Success Response:
  - Code: 200
  - Content:
    - `id`: Internal ID of the record in the [SM2miR Database](http://www.jianglab.cn/SM2miR/).
    - `small_molecule`: Small molecule (or drug) name.
    - `fda_approved`: Indicates with a boolean whether the small molecule or drug is approved by the FDA.
    - `detection_method`: Experimental detection method. The different methods can be: `Northern blot`, `Luciferase reporter assay`, `Illumina HiSeq2000`, `TaqMan low-density array`, `Microarray`, `Northern blot`, `MiRNA PCR array`, `Quantitative real-time PCR` or `Microarray`.
    - `condition`: Tissues or conditions for detection.
    - `pubmed`: URL to the scientific article in the Pubmed database where the evidence that relates miRNA to the small molecule is found.
    - `reference`: Title of the scientific article where the evidence that relates miRNA to the small molecule is found.
    - `expression_pattern`: Expression pattern of miRNA. The different methods can be: `up-regualted`or `down-regualted`.
    - `support`: Brief text with supporting information for this drug-miRNA relationship.
  - Example:
    - URL: <http://localhost:8000/drugs/?mirna=miR-126>*
    - Response:

      ```JSON
        {
          "count":1,
          "next":null,
          "previous":null,
          "results":[
              {
                  "id":275028,
                  "small_molecule":"17beta-estradiol (E2)",
                  "fda_approved":true,
                  "detection_method":"Microarray",
                  "condition":"MCF-7AKT breast cancer cells",
                  "pubmed":"https://pubmed.ncbi.nlm.nih.gov/19528081",
                  "reference":"Estradiol-regulated microRNAs control estradiol response in breast cancer cells.",
                  "expression_pattern":"down-regulated",
                  "support":"To investigate this possibility, we determined microRNA-expression patterns in MCF-7p and MCF-7AKT cells with and without E2 treatment for 4 h. We observed 21 E2-inducible and 7 E2-repressible microRNAs in MCF-7p cells (statistical cutoff P-value <0.05 and fold change >1.5 or <0.7) (Table 1)."
              }
          ]
        }
      ```  

- Error Response:
  - Code: 200
  - Content: empty paginated response (number of elements = 0)
- Additional details: **We are concatenating the 'hsa' prefix for all the drugs records because the file that we are using does not have it and to maintain consistency with the format for mature miRNAs**

### Subscribe to PUBMEDS news

Subscribes an email to our email service that sends news about new Pubmed associated with a miRNA and/or gene.

- URL: `/subscribe-pubmeds/`

- Required query params:
  - `mirna`: miRNA (miRNA code or Accession ID)
  - `email`: valid email address to send the information to
- Optional query params:
  - `gene`: this param allows the user to filter with the miRNA and the gene
- Success Response:
  - Code: 200
  - Content:
    - `token`: subscription token.
- Error Response:
  - Code: 400

### Unsubscribe from PUBMEDS news

Subscribes an email to our email service that sends news about new Pubmed associated with a miRNA and/or gene

- URL: `/unsubscribe-pubmeds/`
- Required query params:
  - `token`: a token that references the subscription
- Success Response:
  - Code: 200
- Error Response:
  - Code: 400

## Considerations

If you use any part of our code, or the tool itself is useful for your research, please consider citing:

```
@article{marraco2021modulector,
  title={Modulector: una plataforma como servicio para el acceso a bases de datos de micro ARNs},
  author={Marraco, Agust{\'\i}n Daniel and Camele, Genaro and Hasperu{\'e}, Waldo and Menazzi, Sebasti{\'a}n and Abba, Mart{\'\i}n and Butti, Mat{\'\i}as},
  journal={Innovaci{\'o}n y Desarrollo Tecnol{\'o}gico y Social},
  volume={3},
  number={1},
  pages={89--114},
  year={2021}
}
```

## Contributing

All the contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Sonarcloud

We are using Sonarcloud to analyze repository code. We are not strictly following all the sonarCloud recommendations but we think that some recommendations will help us to increase quality.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=omics-datascience_modulector&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=omics-datascience_modulector)

## License

This repository is distributed under the terms of the MIT license.

[multiomix-site]: https://multiomix.org/

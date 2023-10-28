# Modulector

Modulector is a performing open platform that provides information about miRNAs and genes based on a compilation of information from different databases. It offers data about:

- [Modulector](#modulector)
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


## Usage

Modulector can be used through the graphical interfaces provided in [Multiomix][multiomix-site], or it can be hosted on your own server (read [DEPLOYING.md](DEPLOYING.md) for more information). We strongly recommend use this software through Multiomix application.

All services are available through a web API accessible from a browser or any other web client. All the responses are in JSON format. In addition to the information provided, sorting, filtering, searching and paging functions are also available. How to use these functions is explained below:


### General

All functions are used as a parameter in the URL. So if you want to access `https://modulector.multiomix.org/service/` by sending parameters to it, just add the following suffix to the end of the URL: `?parameter1=value&parameter2=value&parameter3=value`. The `?` indicates that the parameter section begins, these will be of the form `parameterName=parameterValue` and are separated, in case you need to send more than one, by a `&`.


### Sorting

In order to sort you must specify the parameter `ordering=fieldToSort`, if you want to sort descending you must add a `-` before the field name. You can specify several fields to sort separated by *commas*.

For example, if you want to consume the [miRNA interactions](#mirna-interactions) service by sorting by `score` descending and by `gene` ascending you can access the URL:

`https://modulector.multiomix.org/mirna-interactions/?ordering=-score,gene`


### Filters

To filter it is enough to specify the field and the value by which you want to filter. For example, if you want to consume the [miRNA aliases](#mirna-aliases) service keeping only the aliases of `MIMAT0000062` you could access the following resource:

`https://modulector.multiomix.org/mirna-aliases/?mirbase_accession_id=MIMAT0000062`


### Search

The search is done on the basis of a single parameter called `search` which must contain the value to be searched for. Unlike the filter, the search can be performed on multiple fields at once and is performed by *containing* the search term in the field and is case insensitive (while the filter is by exact value). The fields considered in the search are fixed and will be specified for each service later. For example, the [miRNA interactions](#mirna-interactions) service allows a search by the `gene` field, then the following query could be performed:

`https://modulector.multiomix.org/mirna-aliases/?mirna=hsa-miR-577&search=FO`


### Pagination

Some services can return so many items that paginated responses were chosen, so that they are efficient queries of few items and can be traversed through parameterizable pages. There are two parameters that can be specified to handle pagination:

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

**It will be indicated for each service which fields are available for filtering, sorting and/or searching**.


## Services

### MiRNA target interactions

Receives a miRNA and/or a gene symbol and returns a paginated vector. Each vector entry represents a miRNA-Gene interaction.  
If no gene symbol is entered, all mirna interactions are returned. If a mirna is not entered, all gene interactions are returned. If both are entered, the interaction of mirna with the gene is returned.

- URL: `/mirna-target-interactions`
- Query params:
    - `mirna`: miRNA (Accession ID or name in mirBase) to get its interactions with different genes targets.
    - `gene`: gene symbol to get its interactions with different miRNAs targets.
    - `score`: numerical score to filter the interactions (only interactions with a score greater than or equal to the parameter value are returned). The value of this score is provided by the mirDip database.  
*NOTE*: mirna or gene are required
- Functions:
    - Ordering fields: `gene` and `score`
    - Filtering fields: filtering is not available for this service
    - Searching fields: `gene` 
    - Pagination: yes
- Success Response:
    - Code: 200
    - Content:
        - `id`: internal ID of the interaction.
        - `mirna`: miRNA ID (mirbase MIMAT id or previous ID). The received one as query param.
        - `gene`: target gene.
        - `score`: interaction score (according mirDIP).
        - `source_name`: database from which the interaction was extracted.
        - `pubmeds`: array of pubmed for the miRNA-gene interaction (according to mirTaRBase). 
        - `sources`: miRNA-Gene interaction sources which publish this interaction. mirDIP score is based on the scores of those sources. This field is an array that contains the interaction score source names.
        - `score_class`: `L` (Low), `M` (Medium), `H` (High) or `V` (Very high)
    - Example:
        - URL: http://localhost:8000/mirna-target-interactions?mirna=hsa-miR-891a-5p&gene=EGFR
        - Response:
            ```json
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
                            "https://pubmed.ncbi.nlm.nih.gov/4895700",
                            "https://pubmed.ncbi.nlm.nih.gov/5877664",
                            "https://pubmed.ncbi.nlm.nih.gov/9421182",
                            "https://pubmed.ncbi.nlm.nih.gov/6998431",
                            "https://pubmed.ncbi.nlm.nih.gov/7053609",
                            "https://pubmed.ncbi.nlm.nih.gov/8544338",
                            "https://pubmed.ncbi.nlm.nih.gov/9253007",
                            "https://pubmed.ncbi.nlm.nih.gov/10008540"
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

Returns extra information of a miRNA.

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
        - `aliases`: array of miRNA aliases (previous IDs according to mirBase).
        - `mirna_sequence`: miRNA nucleotide sequence.
        - `mirbase_accession_id`: miRNA accession ID (MIMAT).
        - `links` array of URLs with extra information about this miRNA.
    - Example:
        - URL: http://localhost:8000/mirna?mirna=hsa-miR-548ai
        - Response:
            ```json
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
    - Content: -


### MiRNA aliases

Returns a paginated response with aliases of a miRNA.

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
        - `mirbase_accession_id`: miRNA mirBase accession ID (MIMAT).
        - `mature_mirna`: previous ID (according to mirBase).
    - Example:
        - URL: http://localhost:8000/mirna-aliases?mirbase_accession_id=MIMAT0000062
        - Response:
            ```json
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
    - `limit`: number of elements returned by the service. 50 by default and maximum 3000.   
- Functions:
    - Ordering fields: ordering is not available for this service
    - Filtering fields: filtering is not available for this service
    - Searching fields: searching is not available for this service
    - Pagination: no
- Success Response:
    - Code: 200
    - Content: a list of miRNAs (IDs or accession IDs from miRbase DB) matching the search criteria.
    - Example:
        - URL: http://localhost:8000/mirna-codes-finder?query=hsa-let-7a
        - Response:
            ```json
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

Searches for codes from a list of miRNA identifiers and returns the approved access identifier according to miRbase DB.

- URL: `/mirna-codes` 
- Method: POST
- Required body params (in JSON format):  
    - `mirna_codes`: list of identifiers that you want to get your accession ID from miRbase DB.  
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
        - URL: http://localhost:8000/mirna-codes/
        - body: 
            ```json
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
            ```json
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

Service that takes a text string of any length and returns a list of methylation sites names (loci) containing that search criteria within the Illumina _Infinium MethylationEPIC 2.0_ array.

- URL: `/methylation-sites-finder`
- Method: GET
- Required query params:
    - `query`: Methylation search string.  
- Optional query params:
    - `limit`: number of elements returned by the service. 50 by default and maximum 3000.   
- Functions:
    - Ordering fields: ordering is not available for this service
    - Filtering fields: filtering is not available for this service
    - Searching fields: searching is not available for this service
    - Pagination: no
- Success Response:
    - Code: 200
    - Content: a list of methylation sites from the Illumina 'Infinium MethylationEPIC 2.0' array matching the search criteria.
    - Example:
        - URL: http://localhost:8000/methylation-sites-finder?query=cg25&limit=5
        - Response:
            ```json
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

Searches a list of methylation site names or IDs from different Illumina array versions and returns the name for the _Infinium MethylationEPIC 2.0_ array.

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
        - `methylation_sites`: a JSON object with as many keys as methylation names in the body of the request. For each methylation name, the value is a list of valid methylation names to Illumina _Infinium MethylationEPIC 2.0_ array.
    - Example:
        - URL: http://localhost:8000/methylation-sites/
        - body: 
            ```json
            {
                "methylation_sites":[
                    "cg17771854_BC11",
                    "cg01615704_TC11"
                ]
            }
            ```
        - Response:
            ```json
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
      - Returns a Json with as many keys as there are methylation names/ids in the body. For each methylation name/ID, the value is a list of genes that the name/id methylates.  
    - Example:
        - URL: http://localhost:8000/methylation-sites-genes/
        - body: 
            ```json
            {
                "methylation_sites":[
                    "cg17771854_BC11",
                    "cg22461615_TC11",
                    "name_007"
                ]
            }
            ```
        - Response:
            ```json
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

Returns information of a methylation site.

- URL: `/methylation`
- Required query params:
    - `methylation_site`: methylation_site name from Illumina _Infinium MethylationEPIC 2.0_ array
- Functions:
    - Ordering fields: ordering is not available for this service
    - Filtering fields: filtering is not available for this service
    - Searching fields: searching is not available for this service
    - Pagination: no
- Success Response:
    - Code: 200
    - Content:
        - `name`: name of methylation site.
        - `aliases`: list of other names for the same methylation site on other illumina arrays (EPIC v2, EPIC v1, Methyl450 and Methyl27).
        - `chromosome_position`: information about the chromosome, position and strand on which the site is located.
        - `ucsc_cpg_islands`: List of islands related to the methylation site according to the UCSC database. Each element in the view is a json with the following content:  
            - `cpg_island`: chromosomal coordinates where the island is located.
            - `relation`: Relation of the site to the CpG island. The values it can take are: *Island*=within boundaries of a CpG Island, *N_Shore*=0-2kb 5' of Island, *N_Shelf*=2kb-4kb 5' of Island, *S_Shore*=0-2kb 3' of Island, *S_Shelf*=2kb-4kb 3' of Island.
        - `genes`: The value is a json where each key is a gene that is related to the methylation site. The values for each gene is a list that contains the region of the gene where the methylation site is located. These regions, according to the NCBI RefSeq database, can be: *5UTR*=5' untranslated region between the TSS and ATG start site, *3UTR*=3' untranslated region between stop codon and poly A signal, *exon_#*, *TSS200*=1-200 bp 5' the TSS, *TS1500*=200-1500 bp 5' of the TSS.
    - Example:
        - URL: http://localhost:8000/methylation?methylation_site=cg22461615
        - Response:
            ```json
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

Returns a paginated response of diseases related to a miRNA.

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
        - `id`: internal ID of the record.
        - `category`: disease category.
        - `disease`: disease name.
        - `pubmed`: Pubmed URL.
        - `description`: description about why this miRNA is related to this disease.
    - Example:
        - URL: http://localhost:8000/diseases?mirna=hsa-miR-9500
        - Response:
            ```json
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
- Additional details: **we capitalize the R present in the mirna for each record, because they are mature, however the file does not format it correctly and in the website they show up capitalized**


### Drugs

Returns a paginated response of experimentally validated small molecules (or drugs) effects on miRNA expression.

- URL: `/drugs`
- Method: GET
- Required query params:
    - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.
- Functions:
    - Ordering fields: `condition`, `detection_method`, `small_molecule`, `expression_pattern`, `reference`
      and `support`
    - Filtering fields: `fda_approved` (possible values: `true` or `false`)
    - Searching fields: `condition`, `small_molecule` and `expression_pattern`
    - Pagination: yes
- Success Response:
    - Code: 200
    - Content:
        - `id`: internal ID of the record.
        - `small_molecule`: small molecule (or drug).
        - `fda_approved`: approved by FDA or not.
        - `detection_method`: experimental detection method.
        - `condition`: tissues or conditions for detection.
        - `pubmed`: Pubmed URL.
        - `reference`: reference title.
        - `expression_pattern`: expression pattern of miRNA.
        - `support`: support information for this effect.
    - Example:
        - URL: http://localhost:8000/drugs?mirna=miR-126*
        - Response:
            ```json
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
- Additional details: **we are concatenating the 'hsa' prefix for all the drugs records because the file that we are using does not have it and to maintain consistency with the format for mature miRNAs**


### Subscribe to PUBMEDS news

Subscribes an email to our email service that sends news about new pubmeds associated to a mirna and/or gene

- URL: `/subscribe-pubmeds/`

- Required query params:
    - `mirna`: miRNA (miRNA code or Accession ID)
    - `email`: valid email addres to send the information to
- Optional query params:
    - `gene`: this param allows the user to filter with the mirna and the gene
- Success Response:
    - Code: 200
    - Content:
        - `token`: subscription token.
- Error Response:
    - Code: 400


### Unsubscribe from PUBMEDS news

Subscribes an email to our email service that sends news about new pubmeds associated to a mirna and/or gene

- URL: `/unsubscribe-pubmeds/`
- Required query params:
    - `token`: token that references the subscription
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

We are using sonarcloud to analize repository code. We are not strictly following all the sonarCloud recomendations but we think that some recomendatios will help us to increase quality.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=omics-datascience_modulector&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=omics-datascience_modulector)


## License

This repository is distributed under the terms of the MIT license.


[multiomix-site]: https://multiomix.org/

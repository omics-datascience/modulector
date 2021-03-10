# Modulector Backend

Modulector is a performing open platform that provides information about miRNAs and genes based on a compilation of information from different databases. It offers data about:

- miRNA interactions
- miRNA-target interactions
- Diseases
- Drugs
- miRNA aliases
- Genes aliases


<!-- # Table of Contents
* GET
    * [Mirnas](#mirnas)
    * [Mirna and Gene](#mirna-x-gene)
    * [Mature Mirna](#mature-mirna)
    * [Links](#links)
    * [Diseases](#diseases)
    * [Drugs](#drugs)
    * [Source](#sources) -->



## Usage

All services are available through a web API accessible from a browser or any other web client. In addition to the information provided, sorting, filtering, searching and paging functions are also available. How to use these functions is explained below:


### General

All functions are used as a parameter in the URL. So if you want to access `http://modulector.org/service/` by sending parameters to it, just add the following suffix to the end of the URL: `?parameter1=value&parameter2=value&parameter3=value`. The `?` indicates that the parameter section begins, these will be of the form `parameterName=parameterValue` and are separated, in case you need to send more than one, by a `&`.


### Sorting

In order to sort you must specify the parameter `ordering=fieldToSort`, if you want to sort descending you must add a `-` before the field name. You can specify several fields to sort separated by *commas*.

For example, if you want to consume the [miRNA interactions](#mirna-interactions) service by sorting by `score` descendingly and by `gene` ascendingly you can access the URL:

`http://modulector.org/mirna-interactions/?ordering=-score,gene`


### Filters

To filter it is enough to specify the field and the value by which you want to filter. For example, if you want to consume the [miRNA aliases](#mirna-aliases) service keeping only the aliases of `MIMAT0000062` you could access the following resource:

`http://modulector.org/mirna-aliases/?mirbase_accession_id=MIMAT0000062`


### Search

The search is done on the basis of a single parameter called `search` which must contain the value to be searched for. Unlike the filter, the search can be performed on multiple fields at once and is performed by *containing* the search term in the field and is case insensitive (while the filter is by exact value). The fields considered in the search are fixed and will be specified for each service later. For example, the [miRNA interactions](#mirna-interactions) service allows a search by the `gene` field, then the following query could be performed:

`http://modulector.org/mirna-aliases/?mirna=hsa-miR-577&search=FO`


### Pagination

Some services can return so many items that paginated responses were chosen, so that they are efficient queries of few items and can be traversed through parameterizable pages. There are two parameters that can be specified to handle pagination:

- `page`: allows you to specify the current page. If not specified, the default value `1` is used.
- page_size`: number of elements to return per page. If not specified, the default value `10` is used. The value cannot be greater than `1000`.


### Combining functions

All of the above parameters can be used together! For example, if we wanted to consume the [diseases](#diseases) service by sorting ascending by disease, performing a disease search and keeping only the first 3 items, we could perform the following query (the order of the parameters **does not matter**):

`http://modulector.org/diseases/?ordering=disease&search=leukemia&page_size=3`

**It will be indicated for each service which fields are available for filtering, sorting and/or searching**.


## Services

### Mirna interactions

Returns a paginated response with data about miRNA-Genes interactions.

- URL: `/mirna-interactions`
  
- Required query params
  - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets

- Functions:
  - Ordering fields: `gene` and `score`
  - Filtering fields: filtering is not available for this service
  - Searching fields: `gene`
  - Pagination: Yes

- Success Response:
  - Code: 200
  - Content: 
    - `id`: internal ID of the interaction
    - `mirna`: miRNA
    - `gene`: target gene
    - `score`: interaction score
    - `source_name`: score source name
    - `pubmeds`: array of pubmed for the interaction
    - `sources`: sources that support the interaction
    - `score_class`: `L` (Low), `M` (Medium), `H` (High) or `V` (Very high)
- Error Response:
  - Code: 200
  - Content: empty paginated response (number of elements = 0)


### Mirna target interactions

Returns the information related to the interaction of a gene and a mirna, including related publications and the score related to the interaction.

- URL: `/mirna-target-interactions`
  
- Required query params
  - `mirna`: miRNA identifier (miRNA code or Accession ID)
  - `gene`: gene symbol

- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: No

- Success Response:
  - Code: 200
  - Content: 
    - `id`: internal ID of the interaction
    - `mirna`: miRNA
    - `gene`: target gene
    - `score`: interaction score
    - `source_name`: score source name
    - `pubmeds`: array of pubmed for the interaction
    - `sources`: sources that support the interaction
    - `score_class`: `L` (Low), `M` (Medium), `H` (High) or `V` (Very high)
- Error Response:
  - Code: 404
  - Content: -


```
----
## Mature Mirna
----
    Returns miRNA aliases
* **URL**

  /mirna-aliases

* **Method:**

  `GET`
  
*  **Query Params**
    `mirbase_accession_id=[string]`
    `mature_mirna=[string]`

   **Required:**
   
    **Non Required:**
 

* **Success Response:**

  * **Code:** 200 <br />
  *  **Content:** 
```JSON 
{
  "mirbase_accession_id": "MI0000060",
  "mature_mirna": "hsa-let-7a-1"
}
```


----
## Diseases
----
    Returns disease information related to the mirna, taking into account the first 3 terms that are separated with -
* **URL**

  /diseases

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**
     `mirna=[string]`
   
    **Non Required:**
 


* **Success Response:**

  * **Code:** 200 <br />
  *  **Content:** 
```JSON 
[
  {
      "category": "circulation_biomarker_diagnosis_down",
      "mirna": "hsa-mir-15a",
      "disease": "Leukemia, Lymphocytic, Chronic, B-Cell",
      "pmid": "15737576",
      "description": "Some human miRNAs are linked to leukemias: the miR-15a/miR-16 locus is frequently deleted or down-regulated in patients with B-cell chronic lymphocytic leukemia and miR-142 is at a translocation site found in a case of aggressive B-cell leukemia."
  },
  {
      "category": "circulation_biomarker_diagnosis_down",
      "mirna": "hsa-mir-15a",
      "disease": "Pituitary Neoplasms",
      "pmid": "17028302",
      "description": "Downregulation of miR-15 and miR-16 miRNAs also appears to be a feature of pituitary adenomas."
  }
```

----
## Drugs
----
    Returns drug information, can be filtered by mirna or mirbase id
* **URL**

  /drugs

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**
   
    **Non Required:**
    `mirna=[string]`
    `mirbase_accession_id=[string]`


* **Success Response:**

  * **Code:** 200 <br />
  *  **Content filtered by mirna:**
   
```JSON 
[
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_accession_id": "MIMAT0000068",
      "small_molecule": "Calcitriol",
      "fda_approved": true,
      "detection_method": "Quantitative real-time PCR",
      "condition": "human umbilical vein endothelial cells ",
      "pmid": "24397367",
      "reference": "Vitamin D manipulates miR-181c, miR-20b and miR-16a in human umbilical vein endothelial cells exposed to a diabetic-like environment",
      "expression_pattern": "up-regulated",
      "support": "MiR-181c, miR-15a, miR-20b, miR-411, miR-659, miR-126 and miR-510 were selected for further analysis because they are known to be modified in DM and in other biological disorders."
  },
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_accession_id": "MIMAT0000068",
      "small_molecule": "Benzo(a)pyrene",
      "fda_approved": false,
      "detection_method": "Microarray",
      "condition": "MM plasma cells ",
      "pmid": "24798859",
      "reference": "Regulation of p57-targeting microRNAs by polycyclic aromatic hydrocarbons: Implications in the etiology of multiple myeloma.",
      "expression_pattern": "up-regulated",
      "support": "Here, we report that the environmental carcinogen benzo[a]pyrene (BaP) upregulated the expression of seven p53-targeting miRNAs (miR-25, miR-15a, miR-16, miR-92, miR-125b, miR-141, and miR-200a), while 2,3,7,8-tetrachlorodibenzo-ρ-dioxin (TCDD) upregulated two of them (miR-25 and miR-92) in MM cells"
  }
]
```
*  **Content filtered by mirbase_accession_id:**
```JSON 
[
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_accession_id": "MIMAT0000068",
      "small_molecule": "Calcitriol",
      "fda_approved": true,
      "detection_method": "Quantitative real-time PCR",
      "condition": "human umbilical vein endothelial cells ",
      "pmid": "24397367",
      "reference": "Vitamin D manipulates miR-181c, miR-20b and miR-16a in human umbilical vein endothelial cells exposed to a diabetic-like environment",
      "expression_pattern": "up-regulated",
      "support": "MiR-181c, miR-15a, miR-20b, miR-411, miR-659, miR-126 and miR-510 were selected for further analysis because they are known to be modified in DM and in other biological disorders."
  },
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_accession_id": "MIMAT0000068",
      "small_molecule": "Benzo(a)pyrene",
      "fda_approved": false,
      "detection_method": "Microarray",
      "condition": "MM plasma cells ",
      "pmid": "24798859",
      "reference": "Regulation of p57-targeting microRNAs by polycyclic aromatic hydrocarbons: Implications in the etiology of multiple myeloma.",
      "expression_pattern": "up-regulated",
      "support": "Here, we report that the environmental carcinogen benzo[a]pyrene (BaP) upregulated the expression of seven p53-targeting miRNAs (miR-25, miR-15a, miR-16, miR-92, miR-125b, miR-141, and miR-200a), while 2,3,7,8-tetrachlorodibenzo-ρ-dioxin (TCDD) upregulated two of them (miR-25 and miR-92) in MM cells"
  }
]
```

## Sources
----
    Returns a list of all the database sources we have and the current configuration
* **URL**

  /source

* **Method:**

  `GET`


* **Success Response:**

  * **Code:** 200 <br />
  *  **Content:** 
```JSON 
[
    {
        "id": 20,
        "name": "mirdb",
        "site_url": "http://mirdb.org/index.html",
        "min_score": "70.0000",
        "max_score": "100.0000",
        "score_interpretation": "blabla",
        "description": "blalalala",
        "synchronization_date": "2020-08-20T16:57:23.042752Z",
        "file_type": "csv",
        "file_separator": "\\t",
        "mirnacolumns": [
            {
                "id": 35,
                "position": 1,
                "column_name": "mirna_id",
                "field_to_map": "MIRNA",
                "mirna_source": 20
            },
            {
                "id": 36,
                "position": 2,
                "column_name": "gene",
                "field_to_map": "GEN",
                "mirna_source": 20
            },
            {
                "id": 37,
                "position": 3,
                "column_name": "score",
                "field_to_map": "SCORE",
                "mirna_source": 20
            }
        ]
    }
]
```
----


# POST
## Process
----
  Triggers the processing of the information using the datasource indicated in order to update the database information

* **URL**

  /process

* **Method:**

  `POST`
  
*  **Post Json**
```JSON 
{
    "source_id": 1
}
```
   


* **Success Response:**

  * **Code:** 200 <br />
----
## Create Source
----
    Configures a new source for data import
* **URL**

  /source/create

* **Method:**

  `POST`
*  **Content:** 
```JSON 
{
  "name": "mirdb",
  "site_url": "http://mirdb.org/index.html",
  "min_score": 70,
  "max_score": 100,
  "score_interpretation": "blabla",
  "description": "blalalala",
  "synchronization_date": "2015-02-11T00:00:00.000Z",
  "file_type": "csv",
  "file_separator": "\\t",
  "columns": [
    {
      "position":1,
      "column_name": "bla",
      "field_to_map": "ble"
    },
     {
      "position":2,
      "column_name": "ala",
      "field_to_map": "ale"
    }
  ]
}
```


* **Success Response:**

  * **Code:** 201 <br />
  
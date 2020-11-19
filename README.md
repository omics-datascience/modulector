# Modulector Backend
Python API that provides information about mirnas and genes based on 
a compilation of information of different databases
# Table of Contents
* GET
    * [Mirnas](#mirnas)
    * [Mirna and Gene](#mirna-x-gen)
    * [Mature Mirna](#mature-mirna)
    * [Links](#links)
    * [Diseases](#diseases)
    * [Drugs](#drugs)
    * [Source](#sources)

* POST
    * [Create Source](#create-source)
    * [Process](#process)



# API Definitions
# GET
## Mirnas
  Returns information about the mirnas stored in our database

* **URL**

  /mirna

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**

   `mirna=[string]`
   
    **Non Required:**
 
   
   `page=[integer]`


* **Success Response:**

  * **Code:** 200 <br />
  * **Content:** 
```JSON 
[
  {
            "mirna_code": "hsa-let-7a-2-3p"
  }
]

```
----
## Mirna x Gen
----
    Returns the information related to the interaction of a gen and a mirna,
    including related publications and the score related to the interaction
* **URL**

  /mirnaxgen

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**

     `mirna=[string]`

      `gen=[string]`
   
    **Non Required:**
 
   
   `page=[integer]`


* **Success Response:**

  * **Code:** 200 <br />
  *  **Content:** 
```JSON 
[
  {
      "mirna": "hsa-let-7a-2-3p",
      "gen": "NM_000043",
      "score": "67.1134",
      "pubmed_id": null,
      "pubmed_url": null,
      "name": "mirdb"
  },
]

```
----
## Mature Mirna
----
    Returns the mirbase ID related to the mature mirna provided
* **URL**

  /maturemirna

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
{
  "mirbase_id": "MI0000060",
  "mature_mirna": "hsa-let-7a-1"
}
```

----
## Links
----
    Based on the mirna provided, generates links for different sites that containt aditional information
* **URL**

  /links

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**
     `mirna=[string]`
   
    **Non Required:**

* **Success Response:**

  * **Code:** 200 <br />
  * **Content:** 
```JSON 

[
    {
        "source": "mirdb",
        "url": "http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=hsa-let-7e-5p"
    },
    {
        "source": "rnacentral",
        "url": "https://rnacentral.org/search?q=hsa-let-7e-5p%20species:%22Homo%20sapiens%22"
    },
    {
        "source": "microrna",
        "url": "http://www.microrna.org/linkFromMirbase.do?mirbase=MIMAT0000066"
    },
    {
        "source": "targetscan",
        "url": "http://www.targetscan.org/cgi-bin/mirgene.cgi?mirg=hsa-let-7e-5p"
    },
    {
        "source": "targetminer",
        "url": "http://www.isical.ac.in/~bioinfo_miu/final_html_targetminer/hsa-let-7e-5p.html"
    },
    {
        "source": "quickgo",
        "url": ""
    }
]
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
    `mirbase=[string]`


* **Success Response:**

  * **Code:** 200 <br />
  *  **Content filtered by mirna:**
   
```JSON 
[
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_id": "MIMAT0000068",
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
      "mirbase_id": "MIMAT0000068",
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
*  **Content filtered by mirbase:**
```JSON 
[
  {
      "mature_mirna": "hsa-mir-15a",
      "mirbase_id": "MIMAT0000068",
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
      "mirbase_id": "MIMAT0000068",
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
                "column_name": "gen",
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
  
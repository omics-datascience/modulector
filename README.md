# modulector-backend
Python API that provides information about mirnas and Genes based on 
a compilation of information of different databases
# API Definitions

**Obtain Mirnas**
----
  Returns information about the mirnas stored in our database

* **URL**

  /mirna

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**
     None
   
    **Non Required:**
 
   `mirna=[string]`
   `page=[integer]`


* **Success Response:**

  * **Code:** 200 <br />
  * **Amount of items:** 100
  *  **Content:** 
```JSON 
{
    "count": 1,
    "next": "http://127.0.0.1:8000/mirna?page=2",
    "previous": null,
    "results": [
        {
            "mirna_code": "hsa-let-7a-2-3p"
        }
    ]
}
```

**Obtain Mirnas And Genes**
----
    Returns the information related to the interaction of a gen and a mirna,
    including related publications and the score related to the interaction
* **URL**

  /

* **Method:**

  `GET`
  
*  **Query Params**

   **Required:**
     `mirna=[string]`
   
    **Non Required:**
 
   `gen=[string]`
   `page=[integer]`


* **Success Response:**

  * **Code:** 200 <br />
  * **Amount of items:** 100
  *  **Content:** 
```JSON 
{
    "count": 1921,
    "next": "http://127.0.0.1:8000/?mirna=hsa-let-7a-2-3p&page=2",
    "previous": null,
    "results": [
        {
            "mirna": "hsa-let-7a-2-3p",
            "gen": "NM_000043",
            "score": "67.1134",
            "pubmed_id": null,
            "pubMedUrl": null,
            "name": "mirdb"
        },
    ]
}
```
**Update database information**
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

**Obtain Sources**
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

**Create a source**
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
  
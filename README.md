# Modulector Backend

Modulector is a performing open platform that provides information about miRNAs and genes based on a compilation of information from different databases. It offers data about:

- [miRNA interactions](#mirna-interactions)
- [miRNA-target interactions](#mirna-target-interactions)
- [miRNA details](#mirna-details)
- [miRNA aliases](#mirna-aliases)
- [Diseases](#diseases)
- [Drugs](#drugs)
- Genes aliases


## Usage

<!-- TODO: update Multiomics link when it is online -->
Modulector can be used through the graphical interfaces provided in Multiomics or it can be hosted on your own server (read [DEPLOYING.md](DEPLOYING.md) for more information about the latter option).
All services are available through a web API accessible from a browser or any other web client. All the responses are in *JSON* format. In addition to the information provided, sorting, filtering, searching and paging functions are also available. How to use these functions is explained below:


### General

All functions are used as a parameter in the URL. So if you want to access `http://modulector.org/service/` by sending parameters to it, just add the following suffix to the end of the URL: `?parameter1=value&parameter2=value&parameter3=value`. The `?` indicates that the parameter section begins, these will be of the form `parameterName=parameterValue` and are separated, in case you need to send more than one, by a `&`.


### Sorting

In order to sort you must specify the parameter `ordering=fieldToSort`, if you want to sort descending you must add a `-` before the field name. You can specify several fields to sort separated by *commas*.

For example, if you want to consume the [miRNA interactions](#mirna-interactions) service by sorting by `score` descending and by `gene` ascending you can access the URL:

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
- `page_size`: number of elements to return per page. If not specified, the default value `10` is used. The value cannot be greater than `1000`.

All the paginated responses contain the following fields:

- `count`: total number of elements in Modulector database. This field is useful to compute number of pages (which is equal to `ceil(count / page_size)`).
- `next`: link to the next page.
- `previous`: link to the previous page.
- `results`: array of elements (the structure of each element depends on the service and is explained in detail in the [services](#services) section).


### Combining functions

All of the above parameters can be used together! For example, if we wanted to consume the [diseases](#diseases) service by sorting ascending by disease, performing a disease search and keeping only the first 3 items, we could perform the following query (the order of the parameters **does not matter**):

`http://modulector.org/diseases/?ordering=disease&search=leukemia&page_size=3`

**It will be indicated for each service which fields are available for filtering, sorting and/or searching**.


## Services

### MiRNA interactions

Receives a miRNA ID (mirbase MIMAT ID or previous ID) and returns a paginated vector. Each vector entry represents a miRNA-Gene interaction.

- URL: `/mirna-interactions`
  
- Required query params:
  - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets

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
- Error Response:
  - Code: 200
  - Content: empty paginated response (`count` = 0)


### MiRNA target interactions

Receives a miRNA ID (mirbase MIMAT ID or previous ID) and a gene returns the information about its interaction, including related publications and the interaction score.

- URL: `/mirna-target-interactions`
  
- Required query params:
  - `mirna`: miRNA identifier (miRNA code or Accession ID)
  - `gene`: gene symbol

- Functions:
  - Ordering fields: ordering is not available for this service
  - Filtering fields: filtering is not available for this service
  - Searching fields: searching is not available for this service
  - Pagination: no

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
- Error Response:
  - Code: 404
  - Content: -


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
- Error Response: -


### Diseases

Returns a paginated response of diseases related to a miRNA.

- URL: `/diseases`
  
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
- Error Response:
  - Code: 200
  - Content: empty paginated response (number of elements = 0)


### Drugs

Returns a paginated response of experimentally validated small molecules (or drugs) effects on miRNA expression.

- URL: `/drugs`
  
- Required query params:
  - `mirna`: miRNA (miRNA code or Accession ID) to get its interactions with different targets. If it is not specified, the service returns all the elements in a paginated response.

- Functions:
  - Ordering fields: `condition`, `detection_method`, `small_molecule`, `expression_pattern`, `reference` and `support`
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
- Error Response:
  - Code: 200
  - Content: empty paginated response (number of elements = 0)


## Contributing

All the contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for more information.
library(multiMiR)
db.ver = multimir_dbInfoVersions() # versiones de multimir
db.ver

# cambiar version a la ultima 
vers_table <- multimir_dbInfoVersions()
curr_vers  <- vers_table[1, "VERSION"]  # current version
multimir_switchDBVersion(db_version = curr_vers)

db.tables = multimir_dbTables() # tablas de la db de multimir (dbs integradas)
db.tables

db.info = multimir_dbInfo() # informacion d elas dbs integradas
db.info

# Agrupadores de tablas. Nos interesa en principio "disease.drugs"
predicted_tables()
validated_tables()
diseasedrug_tables()
reverse_table_lookup("targetscan")

db.count = multimir_dbCount() # obtiene registros por base de datos intergadas a multimir
db.count
apply(db.count[,-1], 2, sum)

# Otener listado de todos los genes, drogas, enfermedades y mirnas:
miRNAs   = list_multimir("mirna")
genes    = list_multimir("gene")
drugs    = list_multimir("drug")
diseases = list_multimir("disease")
head(miRNAs)
head(genes)
head(drugs)
head(diseases)

# Ejemplo: obtener informacion para un mirna:
example1 <- get_multimir(mirna = 'hsa-miR-18a-3p', summary = TRUE)
head(example1@data)

# Ejemplo: obtener infoamcion acerca de la droga cisplatin
example2 <- get_multimir(disease.drug = 'cisplatin', table = 'disease.drug')
head(example2@data)

# Pruebas Mauri
miRNAs = list_multimir("mirna") # obtengo todos los mirnas
human_miRNAs <- subset(miRNAs, org == "hsa") # filtro los mirnas humanos

all_mirna_drugs <- list() # aca guardo resultados

# Itero por cada mirna humano para obtener informacion de drogas
for (mirna in human_miRNAs$mature_mirna_id) {
  print(mirna)
  mirna_drugs <- get_multimir(mirna=mirna, table="disease.drug", summary = FALSE) # table="all" tampoco da lo que necesitmos
  
  # Store drugs for this miRNA
  all_mirna_drugs[[mirna]] <- mirna_drugs@data$disease_drug
}

# Intento de otra forma:
drugs = list_multimir("drug") # Obtengo todas las drogas dispnibles

all_mirna_drugs <- list() # aca guardo resultados

# Itero por cada droga para obtener informacion de mirnas
for (d in drugs$drug) {
  mirna_drugs <- get_multimir(disease.drug = d, table = 'disease.drug', summary = TRUE) # table="all" tampoco da lo que necesitmos
  
  # Store drugs for this miRNA
  all_mirna_drugs[[d]] <- mirna_drugs@data$mature_mirna_id
}

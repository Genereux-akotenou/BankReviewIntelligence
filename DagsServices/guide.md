### Instructions

Pour utiliser les DAGs développés ici, deux options s'offrent à vous :

1. **Copier-Coller les DAGs**
   - Copiez les fichiers `dags.py` dans le dossier `dags` de votre installation locale d'Airflow.
   - Adaptez les chemins des fichiers à exécuter à l'intérieur de chaque DAG.

2. **Docker based**
    - Utiliser le repertoire Volume de docker 
    - Copier et coller les dags dans le repertoire dags de ce volume

### Structure des DAGs
1. **DAG 0: Extraction Initiale**
   - **Description**: Ce DAG effectue une extraction initiale des données à partir de Maps.
   - **Fréquence**: Exécution unique pour l'initialisation des données.
   
2. **DAG 1: Extraction Récurrente**
   - **Description**: Ce DAG effectue une extraction récurrente des données tous les deux jours.
   - **Fréquence**: Toutes les 48 heures (2 jours).
   
3. **DAG 2: Prétraitement et Stockage**
   - **Description**: Ce DAG gère le prétraitement des données et leur stockage dans une macro working table.
   - **Fréquence**: Selon les besoins de mise à jour des données prétraitées.
   
4. **DAG 3: ETL vers le Data Warehouse**
   - **Description**: Ce DAG effectue les opérations ETL pour transférer les données vers le Data Warehouse.
   - **Fréquence**: Selon les besoins de synchronisation avec le Data Warehouse.

### Instructions de Configuration
1. **Chemins des Fichiers**
   - Assurez-vous de mettre à jour les chemins des fichiers à exécuter à l'intérieur de chaque DAG pour correspondre à votre environnement local.
   
2. **Dossier des DAGs**
   - Placez les fichiers DAGs dans le dossier `dags` de votre installation Airflow : `[AIRFLOW_HOME]/dags/`.

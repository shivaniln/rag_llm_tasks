# East India Geo-Assistant



## 1. Project Overview



The East India Geo-Assistant is a proof of concept (PoC) for a local Retrieval-Augmented Generation (RAG) system. It is designed to answer questions about school admissions and geography using document-based information and geospatial data served through GeoServer.



The system uses Elasticsearch for indexing and retrieval, a locally running language model for generation, embedding models for semantic search, a cross-encoder for reranking, and GeoServer for accessing geographic features.



### Objectives



- Prepare a local development environment for RAG.

- Secure Elasticsearch and GeoServer access.

- Load and evaluate local language and retrieval models.

- Make school, road, and land-use data available through GeoServer.

- Develop an ingestion and retrieval pipeline with evidence-based answers.

- Evaluate retrieval quality, confidence, and answer reliability.



### Execution Environment



- Operating system: Windows

- Project directory: `C:\\geoassistant`

- Python virtual environment: `.venv`

- Elasticsearch and Kibana: Docker Compose

- Language model runtime: Ollama

- Geospatial server: GeoServer





## 2. Software Versions and Models



### 2.1 Software Environment

| Component | Version / Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.12.10 |
| Elasticsearch | 8.19.0 |
| Kibana | 8.19.0 |
| GeoServer | 3.0.1 |
| Ollama | 0.40.4 |
| Docker Engine | 29.8.2 |
| Docker Desktop | 4.94.0 |
| Python environment | `.venv` |
| Elasticsearch JVM heap | 1 GB initial and maximum heap |

### 2.2 Local Language Model

| Property | Value |
|---|---|
| Model | `qwen2.5:3b` |
| Parameter count | Approximately 3 billion |
| Quantisation | Q4_K_M |
| Context length | 32,768 tokens (model configuration) |
| Active context during test | 4,096 tokens |
| Model size | Approximately 2.2 GB |
| Generation speed | Approximately 16.43 tokens/second |
| Prompt evaluation speed | Approximately 55.26 tokens/second |
| Execution | Local through Ollama, CPU |

The model was tested with the internet disconnected to verify that local inference works without an external AI API.

### 2.3 Embedding and Reranking Models

| Model | Purpose | Output |
|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | Text embeddings | 384-dimensional vectors |
| `intfloat/e5-small-v2` | Text embeddings | 384-dimensional vectors |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranking | Raw relevance score |


The models loaded successfully in Python. The cross-encoder test returned a score of `-9.120125`. This is a raw score, not a calibrated probability.



### 2.4 Python Dependencies



Python dependencies and their pinned versions are recorded in `requirements.txt`, generated using `pip freeze`.



Key dependencies include Elasticsearch, GeoPandas, NumPy, NetworkX, PyProj, scikit-learn, Sentence Transformers, Shapely, Streamlit, and PyTorch.





## 3. Service Ports and Startup Commands



### 3.1 Service Endpoints

| Service | Local URL | Port |
|---|---|---:|
| Elasticsearch | `http://localhost:9200` | 9200 |
| Kibana | `http://localhost:5601` | 5601 |
| GeoServer | `http://localhost:8080/geoserver` | 8080 |
| Ollama API | `http://localhost:11434` | 11434 |



### 3.2 Start Elasticsearch and Kibana



Open PowerShell and navigate to the project directory:



```powershell

cd C:\\geoassistant

```



Set the Elasticsearch and Kibana passwords as environment variables using secure prompts. Do not place password values in source files.



```powershell

$secure = Read-Host "Enter Elasticsearch password" -AsSecureString

$env:ELASTIC\_PASSWORD = \[System.Net.NetworkCredential]::new("", $secure).Password



$secure = Read-Host "Enter Kibana password" -AsSecureString

$env:KIBANA\_PASSWORD = \[System.Net.NetworkCredential]::new("", $secure).Password



Remove-Variable secure

docker compose up -d

```



Check the running containers:



```powershell

docker compose ps

```



These environment variables must be set again in a new PowerShell session before starting the services if they are not otherwise configured.



### 3.3 Start the Python Environment



```powershell

cd C:\\geoassistant

.\\.venv\\Scripts\\Activate.ps1

```



Install pinned dependencies if setting up the project on a new environment:



```powershell

pip install -r requirements.txt

```



### 3.4 Start GeoServer



GeoServer 3.0.1 was extracted to `C:\\geoserver-extract`.



Open a separate PowerShell terminal and run:



```powershell

$env:JAVA\_HOME = "C:\\Program Files\\Java\\jdk-17"

$env:GEOSERVER\_HOME = "C:\\geoserver-extract"

$env:GEOSERVER\_DATA\_DIR = "C:\\geoserver-extract\\data\_dir"



Set-Location C:\\geoserver-extract\\bin

.\\startup.bat

```



Keep the terminal open while GeoServer is running.



### 3.5 Start Ollama



Ensure Ollama is running on the local machine. Start it if necessary:



```powershell

ollama serve

```



In another terminal, run the local model:



```powershell

ollama run qwen2.5:3b

```



Ollama exposes its local API on port 11434 by default.





## 4. Data Sources and Security



### 4.1 Data Sources



\*\*School data\*\*



- Source: `schools.gpkg`

- Format: GeoPackage

- Coordinate reference system: EPSG:4326

- Features: 1,062

- Geometry: MultiPolygon

- Attributes: `osm\_id`, `code`, `fclass`, `name`, `type`, and `geometry`

- The dataset contains OpenStreetMap building footprints classified as schools. It does not contain school board, seat availability, or admission cut-off information.



\*\*Road and land-use data\*\*



Road and land-use features were extracted from a Geofabrik OpenStreetMap dataset because separate assessment datasets for these layers were unavailable during setup.



- `roads.gpkg`: approximately 1,516,111 features

- `landuse.gpkg`: approximately 89,730 features



These datasets are provided through the `east\_india` GeoServer workspace.



### 4.2 GeoServer Access



GeoServer is configured with the `east\_india` workspace and the following published layers:



- `east\_india:schools`

- `east\_india:roads`

- `east\_india:landuse`



The `rag\_geo` user has read access to the workspace layers. Unauthenticated access was tested and refused, while authenticated WFS requests successfully returned GeoJSON.



Write access is not granted to `rag\_geo`; a WFS update attempt was rejected.



### 4.3 Elasticsearch Access



Elasticsearch security is enabled. The `rag\_app` role and `rag\_app\_key` are intended for application access to the following indices only:



- `east\_india\_chunks`

- `east\_india\_entities`

- `east\_india\_relations`



The API key successfully searched the permitted `east\_india\_chunks` index. Attempts to access cluster health and search an unrelated index returned HTTP 403 Forbidden.



The application must use the restricted API key rather than the `elastic` superuser.



### 4.4 Secret Management



- Credentials and the Elasticsearch API key are stored in `.env`.

- `.env` is listed in `.gitignore`.

- `git check-ignore .env` confirmed that the file is ignored.

- `git ls-files .env` returned no results, confirming that `.env` is not tracked by Git.

- Actual passwords, API-key secrets, and other credentials must never be included in submitted documentation or source files.





## 5. Verification Results and Current Limitations



### 5.1 Environment and Security Tests

| Check | Result |
|---|---|
| Elasticsearch authentication | Passed |
| Single-node cluster health | Yellow; no unassigned primary shards |
| Restricted API key can search its permitted index | Passed |
| Restricted API key cannot access cluster health | Passed; HTTP 403 |
| Restricted API key cannot search an unrelated index | Passed; HTTP 403 |
| `.env` ignored by Git | Passed |
| `.env` not tracked by Git | Passed |
| Offline local language model response | Passed |
| Both embedding models load successfully | Passed |
| Cross-encoder reranker produces a score | Passed |
| Anonymous GeoServer access refused | Passed; HTTP 401 |
| Authenticated GeoServer WFS GeoJSON request | Passed |
| GeoServer write attempt by `rag_geo` | Rejected |



### 5.2 Model Test Results



The local language model produced a response with the internet disconnected. The measured prompt evaluation speed was approximately 55.26 tokens per second, and generation speed was approximately 16.43 tokens per second.



Both embedding models produced 384-dimensional vectors. The cross-encoder produced a raw score of `-9.120125` in the test.



These measurements are specific to the tested machine and configuration and may vary between runs.



### 5.3 Current Limitations



The supplied school dataset contains geographic building footprints and basic OpenStreetMap attributes, not admissions information such as board, available seats, or cut-off marks.



Road and land-use datasets were substituted with data extracted from OpenStreetMap because the corresponding assessment datasets were unavailable during setup. This substitution must be disclosed in the final submission.



The environment and access-control checks do not by themselves demonstrate a complete RAG application. Entity extraction, entity resolution, vector ingestion and evaluation, graph relationships, retrieval modes, reranking evaluation, confidence calibration, and end-to-end answer generation remain to be implemented and tested.





## 6. Algorithm Notes



The following algorithms are relevant to the planned RAG pipeline. Their implementation and evaluation must be completed and verified before the final submission.



### 6.1 BM25



BM25 is a lexical retrieval algorithm that ranks documents using query-term frequency, inverse document frequency, and document-length normalization. It is used to find passages containing terms relevant to a query.



### 6.2 HNSW



Hierarchical Navigable Small World (HNSW) is an approximate nearest-neighbour search algorithm. It organizes vectors into a navigable graph to find similar vectors efficiently without comparing every vector in the index. Its search accuracy and latency depend on index and search parameters.



### 6.3 Reciprocal Rank Fusion



Reciprocal Rank Fusion (RRF) combines rankings from multiple retrieval methods. Each result receives a contribution based on its rank in each list, allowing lexical and semantic retrieval results to be combined without requiring their raw scores to share the same scale.



### 6.4 Cross-Encoder



A cross-encoder processes a query and a candidate passage together and produces a relevance score. It can improve candidate ordering after initial retrieval, but scoring candidates individually is more expensive than retrieving them using a vector index.



### 6.5 Softmax with Temperature



Softmax converts a set of scores into normalized values. Temperature controls how concentrated or distributed those values are: lower temperatures produce sharper distributions, while higher temperatures produce flatter distributions. Such values should not automatically be interpreted as calibrated confidence.



### 6.6 Greedy Decoding



Greedy decoding selects the highest-scoring next token at each generation step. It is deterministic for fixed inputs and settings when the model and runtime behave deterministically. It is useful for repeatable extraction and answer-generation experiments.



### 6.7 Graph Traversal



Graph traversal follows relationships between entities, such as a school and a locality or a school and a relevant rule. Traversal limits, cycle detection, and fan-out controls help prevent excessively large or repetitive searches.



\*\*Implementation status:\*\* These notes describe the algorithms required by the assessment. Their actual use, parameter settings, and evaluation results must be documented after the corresponding pipeline stages are implemented.



## 7. Disclosures and Third-Party Components



### 7.1 Software and Libraries



The project uses open-source software and libraries, including Python, Elasticsearch, Kibana, GeoServer, Ollama, Docker, GeoPandas, NumPy, NetworkX, PyProj, scikit-learn, Sentence Transformers, Shapely, Streamlit, and PyTorch. Exact Python dependency versions are recorded in `requirements.txt`.



### 7.2 Models



The following models were used for local testing:



- `qwen2.5:3b` for local language generation.

- `sentence-transformers/all-MiniLM-L6-v2` for embeddings.

- `intfloat/e5-small-v2` for embeddings.

- `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking.



These were selected as alternatives because the supplied model identifiers were not available in the assessment materials reviewed during setup. This substitution should be confirmed against the assessor's instructions before final submission.



### 7.3 Geospatial Data



The school GeoPackage was inspected using GeoPandas. Roads and land-use layers were derived from OpenStreetMap data obtained through Geofabrik because separate assessment files for those layers were unavailable during setup.



The use of these substitute datasets must be disclosed, including their source and any relevant attribution requirements.



### 7.4 Development Assistance



AI assistance was used for environment setup, troubleshooting, command guidance, and drafting documentation. The submitted implementation, evaluation code, and algorithm choices must be reviewed and understood by the project author, who must be able to explain and modify them during the assessment.



### 7.5 Security and Reproducibility



No passwords, API-key secrets, or personal credentials should be included in the submitted files. Secrets are kept in environment variables or `.env`, and `.env` is excluded from Git tracking.



The project must be accompanied by the pinned dependency list, startup instructions, evaluation results, and other artifacts needed to reproduce the completed implementation.



## 8. References



- The supplied \*Problem Statement for Intern Assessment: AI/ML RAG \& LLM App Development\*.

- Official documentation for the software, libraries, and models used.

- OpenStreetMap and Geofabrik documentation and attribution requirements for the substituted geospatial datasets.




## 9. Task 8 â€” Pipeline, Safety, and Interface

### 9.1 End-to-End Pipeline
Implemented `app/pipeline.py` to connect entity extraction, hybrid retrieval, cross-encoder reranking, confidence signals, and local LLM generation using Ollama.

The pipeline returns a structured JSON response containing the answer, citations, confidence, entities used, graph paths, and settings.

### 9.2 Grounded Generation and Citations
The generation prompt instructs the model to use only retrieved sources and treat their contents as untrusted data. The response is parsed as JSON, and citation IDs are checked against the retrieved chunk IDs. Invalid citations cause the response to abstain.

### 9.3 Abstention and Safety
The pipeline abstains when no candidates are available or confidence falls below the configured fallback threshold. Requests matching basic rules for data modification or secret disclosure are rejected.

The current threshold of 0.5 is a temporary fallback, not a calibrated threshold. Calibration could not be completed because labeled calibration questions are unavailable.

### 9.4 Smoke Test
A test question, "What is the East India Geo-Assistant assessment?", returned an answer describing the assessment and cited retrieved chunk `e51f23cd53fdb6ee8188`.

The returned confidence was approximately 0.998. This value is uncalibrated and must not be interpreted as a verified probability of correctness.

### 9.5 Interface
The Streamlit interface is implemented in `app/ui.py`. It displays the answer, confidence, citations, entities, graph paths, and pipeline settings. Verify the interface manually before recording the UI test as passed.

### 9.6 Evaluation Status
The current text corpus contains 39 chunks from the assessment PDF. No valid development questions, calibration questions, or labeled retrieval judgments are available. Therefore, a valid ten-question accuracy evaluation, calibrated confidence evaluation, and before-and-after failure analysis have not been completed.

The current graph contains spatial school-road proximity relations. Graph expansion is not yet integrated into retrieval.


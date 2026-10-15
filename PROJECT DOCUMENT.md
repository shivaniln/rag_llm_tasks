# East India Geo-Assistant: Project Document

## 1. Overview

The East India Geo-Assistant is a proof of concept (PoC) for a local Retrieval-Augmented Generation (RAG) system. It answers questions about school admissions and geography using document passages and geospatial data served through GeoServer. Everything runs locally on Windows with free and open-source software.

Components: Elasticsearch (indexing and retrieval), a local language model via Ollama (generation), two embedding models (semantic search), a cross-encoder (reranking), and GeoServer (geographic features).

- Project directory: `C:\geoassistant`
- Python virtual environment: `.venv`
- Elasticsearch and Kibana: Docker Compose

## 2. Completion Status

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Area</th><th>Status</th></tr>
<tr><td>Task 1: environment, security, models, GeoServer</td><td>Completed and verified (section 5)</td></tr>
<tr><td>Task 2: entity extraction and evaluation</td><td>Not completed. No gold entity file was available</td></tr>
<tr><td>Task 3: embedding comparison, index tuning, approximate-vs-exact, paging</td><td>Not completed as a formal evaluation. Embeddings and a 39-chunk index exist and are used by the pipeline</td></tr>
<tr><td>Task 4: graph relations</td><td>Partial. Spatial school-to-road proximity relations exist. Text-based relations, graph measures and <code>expand()</code> in retrieval are not completed</td></tr>
<tr><td>Task 5: retrieval metrics, k choice, tuning</td><td>Not completed. No labelled retrieval judgments were available</td></tr>
<tr><td>Task 6: reranking evaluation</td><td>Not completed as an evaluation. A cross-encoder is used in the pipeline</td></tr>
<tr><td>Task 7: calibration, abstention threshold, sampling consistency</td><td>Not completed. No labelled calibration or development questions were available. A fallback threshold of 0.5 is used</td></tr>
<tr><td>Task 8: pipeline, safety, interface</td><td>Implemented. Evaluation on ten development questions not completed (section 7)</td></tr>
</table>

Reason for the gaps: the evaluation files (`gold_entities.jsonl`, `retrieval_judgments.jsonl`, `calibration_questions.jsonl`, `dev_questions.jsonl`), the document corpus, and separate roads and landuse files were not among the materials available during setup.

## 3. Software, Models and Ports

### 3.1 Software

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Component</th><th>Version / configuration</th></tr>
<tr><td>Operating system</td><td>Windows</td></tr>
<tr><td>Python</td><td>3.12.10</td></tr>
<tr><td>Elasticsearch</td><td>8.19.0 (single node, 1 GB initial and maximum heap)</td></tr>
<tr><td>Kibana</td><td>8.19.0</td></tr>
<tr><td>GeoServer</td><td>3.0.1 (JDK 17)</td></tr>
<tr><td>Ollama</td><td>0.40.4</td></tr>
<tr><td>Docker Engine / Desktop</td><td>29.8.2 / 4.94.0</td></tr>
</table>

Pinned Python dependencies are in `requirements.txt` (`pip freeze`). Key libraries: Elasticsearch client, GeoPandas, NumPy, NetworkX, PyProj, scikit-learn, Sentence Transformers, Shapely, Streamlit, PyTorch.

### 3.2 Language model

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Property</th><th>Value</th></tr>
<tr><td>Model</td><td><code>qwen2.5:3b</code></td></tr>
<tr><td>Parameters</td><td>approximately 3 billion</td></tr>
<tr><td>Quantisation</td><td>Q4_K_M</td></tr>
<tr><td>Context length</td><td>32,768 tokens (model configuration); 4,096 active during the test</td></tr>
<tr><td>Model size</td><td>approximately 2.2 GB</td></tr>
<tr><td>Generation speed</td><td>approximately 16.43 tokens/second</td></tr>
<tr><td>Prompt evaluation speed</td><td>approximately 55.26 tokens/second</td></tr>
<tr><td>Execution</td><td>Local through Ollama, on CPU</td></tr>
</table>

Local inference was tested with the internet disconnected.

### 3.3 Embedding and reranking models

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Model</th><th>Purpose</th><th>Output</th></tr>
<tr><td><code>sentence-transformers/all-MiniLM-L6-v2</code></td><td>Embeddings</td><td>384-dimensional vectors</td></tr>
<tr><td><code>intfloat/e5-small-v2</code></td><td>Embeddings</td><td>384-dimensional vectors</td></tr>
<tr><td><code>cross-encoder/ms-marco-MiniLM-L-6-v2</code></td><td>Reranking</td><td>Raw relevance score (a test pair returned -9.120125)</td></tr>
</table>

The cross-encoder score is a raw logit, not a calibrated probability. A sigmoid is needed to turn it into a 0 to 1 value. E5 models expect `query: ` and `passage: ` prefixes.

These models were used because the supplied model identifiers were not found in the materials reviewed during setup.

### 3.4 Ports

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Service</th><th>URL</th><th>Port</th></tr>
<tr><td>Elasticsearch</td><td><code>http://localhost:9200</code></td><td>9200</td></tr>
<tr><td>Kibana</td><td><code>http://localhost:5601</code></td><td>5601</td></tr>
<tr><td>GeoServer</td><td><code>http://localhost:8080/geoserver</code></td><td>8080</td></tr>
<tr><td>Ollama API</td><td><code>http://localhost:11434</code></td><td>11434</td></tr>
</table>

## 4. Start-up Commands

**Elasticsearch and Kibana** (passwords are entered at a prompt and never stored in files):

```powershell
cd C:\geoassistant
$secure = Read-Host "Enter Elasticsearch password" -AsSecureString
$env:ELASTIC_PASSWORD = [System.Net.NetworkCredential]::new("", $secure).Password
$secure = Read-Host "Enter Kibana password" -AsSecureString
$env:KIBANA_PASSWORD = [System.Net.NetworkCredential]::new("", $secure).Password
Remove-Variable secure
docker compose up -d
docker compose ps
```

Set these variables again in every new PowerShell session before starting the services.

**Python environment:**

```powershell
cd C:\geoassistant
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**GeoServer** (extracted to `C:\geoserver-extract`, separate terminal, keep open):

```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:GEOSERVER_HOME = "C:\geoserver-extract"
$env:GEOSERVER_DATA_DIR = "C:\geoserver-extract\data_dir"
Set-Location C:\geoserver-extract\bin
.\startup.bat
```

**Ollama:**

```powershell
ollama serve
ollama run qwen2.5:3b
```

**Interface:**

```powershell
streamlit run app/ui.py
```

## 5. Task 1: Environment and Security Results

### 5.1 Cluster health

The single-node cluster status is **yellow** with no unassigned primary shards. Each index has one primary shard and, by default, one replica. A replica cannot be placed on the same node as its primary, so the replica stays unassigned. Data is complete, but there is no redundancy. Setting `number_of_replicas` to 0 on an index would make it green.

### 5.2 Index naming

Elasticsearch does not allow spaces or capital letters in index names. The three indices from the brief are therefore named `east_india_chunks`, `east_india_entities` and `east_india_relations`.

### 5.3 Access control

- Elasticsearch security is enabled. The role `rag_app` and API key `rag_app_key` are for application access to the three indices above only. The application uses this key, not the `elastic` superuser.
- GeoServer has the workspace `east_india` with layers `schools`, `roads` and `landuse`. The user `rag_geo` has read access to the workspace.
- Secrets are kept in `.env`, which is listed in `.gitignore`. `git check-ignore .env` confirmed it is ignored and `git ls-files .env` returned nothing, so it is not tracked.

### 5.4 Verification results

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Check</th><th>Result</th></tr>
<tr><td>Elasticsearch authentication</td><td>Passed</td></tr>
<tr><td>API key searches its permitted index <code>east_india_chunks</code></td><td>Passed</td></tr>
<tr><td>API key on cluster health</td><td>Refused (HTTP 403)</td></tr>
<tr><td>API key on an unrelated index</td><td>Refused (HTTP 403)</td></tr>
<tr><td><code>.env</code> ignored and not tracked by Git</td><td>Passed</td></tr>
<tr><td>Language model answers offline</td><td>Passed</td></tr>
<tr><td>Both embedding models load, 384-dimensional output</td><td>Passed</td></tr>
<tr><td>Cross-encoder returns a score</td><td>Passed</td></tr>
<tr><td>Anonymous GeoServer request</td><td>Refused (HTTP 401)</td></tr>
<tr><td>Authenticated WFS request returns GeoJSON</td><td>Passed</td></tr>
<tr><td>Write attempt by <code>rag_geo</code></td><td>Rejected</td></tr>
</table>

Measurements are specific to the tested machine and may vary between runs.

## 6. Data Provenance

**Schools (supplied):** `schools.gpkg`, GeoPackage, EPSG:4326, 1,062 features, MultiPolygon geometry, attributes `osm_id`, `code`, `fclass`, `name`, `type`, `geometry`. These are OpenStreetMap building footprints classified as schools. The file has no board, seat availability or cut-off information.

**Roads and land use (substituted):** separate files for these layers were not available during setup, so they were extracted from a Geofabrik OpenStreetMap dataset. `roads.gpkg` has approximately 1,516,111 features and `landuse.gpkg` approximately 89,730. Both are published in the `east_india` GeoServer workspace.

Attribution: © OpenStreetMap contributors (Open Database License).

## 7. Task 8: Pipeline, Safety and Interface

### 7.1 Pipeline

`app/pipeline.py` connects entity extraction, hybrid retrieval, cross-encoder reranking, confidence signals and generation with the local model through Ollama. It returns JSON containing the answer, citations, confidence, entities used, graph paths and settings.

### 7.2 Grounded generation and citations

The prompt tells the model to answer only from retrieved sources and to treat their contents as untrusted data. The response is parsed as JSON and each cited chunk ID is checked against the retrieved chunk IDs. If a citation was not retrieved, the pipeline abstains rather than returning the answer.

### 7.3 Abstention and safety

The pipeline abstains when no candidates are found or when confidence is below the threshold. The threshold of 0.5 is a temporary fallback. It is **not calibrated**, because no labelled calibration questions were available. Requests matching basic rules for data modification or secret disclosure are rejected.

### 7.4 Smoke test

The question "What is the East India Geo-Assistant assessment?" returned an answer describing the assessment, citing retrieved chunk `e51f23cd53fdb6ee8188`. The confidence was about 0.998. This value is uncalibrated and is not a verified probability of correctness. The question is also answered by the same document that was indexed, so it is an easy case.

### 7.5 Interface

`app/ui.py` is a Streamlit interface showing the answer, confidence, citations, entities, graph paths and settings.

## 8. Algorithm Notes

<table border="1" cellpadding="6" cellspacing="0">
<tr><th>Algorithm</th><th>Explanation</th><th>Where it is used</th></tr>
<tr><td>BM25</td><td>Lexical ranking from query-term frequency, inverse document frequency and document-length normalisation</td><td>Keyword part of the hybrid retrieval over <code>east_india_chunks</code></td></tr>
<tr><td>HNSW</td><td>Approximate nearest-neighbour search over a layered graph of vectors, avoiding comparison with every vector. Accuracy and latency depend on build and search parameters</td><td>Vector search through Elasticsearch <code>dense_vector</code> indexing (384 dimensions). Its parameters were not tuned or compared</td></tr>
<tr><td>Reciprocal Rank Fusion</td><td>Combines rankings by summing 1/(constant + rank) per list, so lexical and vector scores need no common scale</td><td>Fusion of keyword and vector lists in the hybrid mode. The constant was not tuned</td></tr>
<tr><td>Cross-encoder</td><td>Reads query and passage together and scores the pair. More accurate than a bi-encoder but needs one pass per pair, so it is applied only to a shortlist</td><td>Reranking in <code>app/pipeline.py</code> with <code>ms-marco-MiniLM-L-6-v2</code>. Its raw score feeds the confidence signals</td></tr>
<tr><td>Softmax with temperature</td><td>Converts scores to normalised values. Lower temperature gives a sharper distribution and higher gives a flatter one. The outputs are not automatically calibrated confidence</td><td>Not used for calibration, since temperature scaling was not completed</td></tr>
<tr><td>Greedy decoding</td><td>Picks the highest-probability token at each step, giving repeatable output for fixed inputs. Repeatable does not mean correct</td><td>Language-model generation settings in the pipeline</td></tr>
<tr><td>Graph traversal</td><td>Follows relations between entities, with cycle detection and fan-out limits to avoid repeated or very large searches</td><td>A school-road proximity graph exists. Traversal and expansion are not integrated into retrieval</td></tr>
</table>

## 9. Evaluation Status and Limitations

- The text corpus holds 39 chunks from the assessment PDF only. It has no admissions circulars, so the system cannot yet answer real admission questions.
- No valid development questions, calibration questions or retrieval judgments were available. Therefore these are **not done**: the ten-question accuracy evaluation, retrieval metrics (precision, recall, MRR, nDCG), calibration (ECE, Brier), the abstention threshold, and the failure analysis with a fix.
- The entity extractors, entity resolution and `east_india_entities` index are not completed. The graph has only spatial school-road relations.
- The school data has no board, seats or cut-off, so questions on these cannot be answered from the data.
- Roads and land use are substituted OpenStreetMap data, and the road layer is very large (about 1.5 million features).
- The 3-billion-parameter local model runs on CPU at about 16 tokens/second and can still produce unsupported answers.

**Next steps with more time and data:** obtain or build a document corpus and labelled evaluation files, complete Tasks 2 to 7 with measured results, integrate graph expansion into retrieval, and calibrate the abstention threshold.

## 10. Disclosures

- **Software:** Python, Elasticsearch, Kibana, GeoServer, Ollama, Docker, GeoPandas, NumPy, NetworkX, PyProj, scikit-learn, Sentence Transformers, Shapely, Streamlit, PyTorch. Exact versions are in `requirements.txt`.
- **Models:** `qwen2.5:3b`, `sentence-transformers/all-MiniLM-L6-v2`, `intfloat/e5-small-v2`, `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Data:** `schools.gpkg` (supplied). Roads and land use from Geofabrik OpenStreetMap extracts. Attribution: © OpenStreetMap contributors.
- **AI assistance:** an AI assistant (Claude) was used for environment setup, troubleshooting, command guidance and drafting documentation. The author reviewed the implementation and is responsible for it.
- **Secrets:** no passwords or API keys are included in submitted files. They are held in environment variables or `.env`, which is excluded from Git.

## 11. References

- Problem statement: *Intern Assessment: AI/ML RAG & LLM App Development*.
- Official documentation of the software, libraries and models above.
- OpenStreetMap and Geofabrik documentation.

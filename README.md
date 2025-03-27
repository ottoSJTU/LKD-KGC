### Overview

This is the code implementation of the ECML-PKDD 2025 submission paper "LKD-KGC: Domain-Specific KG Construction via LLM-driven Knowledge Dependency Parsing"

### Usage

- **Environment Setup**

```
!pip install -r requirements.txt  
```

- **Data Preparation**: The preprocessed Prometheus documentation dataset used in the paper is stored in `./data/prometheus_documents/` as example. Users may also prepare their own datasets as input.

- **Running the Code**

  - The  major code is organized in the Jupyter notebook file `main.ipynb`.

  - Modify the second code block in the file to specify:

    ```
    os.environ["OPENAI_API_KEY"] = "your_api_key"  
    DEFAULT_MODEL = "your_LLM"  
    DATA_PATH = "your_document_path"  
    OUTPUT_PATH = "your_output_path"  
    ```

  - Execute all code blocks.


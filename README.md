# ToolCharm API Pack

Welcome to API Pack, a comprehensive multilingual dataset designed to significantly advance the API call generation capabilities of ToolCharm's base REST api calling model. The base_model_gen folder contains specially modified versions of the 
openapi-snipper and openapi-sampler packages which not only generate snippets for each endpoint but do so with specific and type-appropriate dummy data.

# Getting Started

To get started, simply clone this repository and run the following command from inside `base_model_gen`:

```bash
npm install
```

Then, copy the two folders in the `modified node packages` folder to the `node_modules` folder in the root directory of your project. This will replace the existing openapi-snipper and openapi-sampler packages with the modified versions which generate detailed dummy data.

# Usage

1. In`step 1/`, create a scraped_specs folder and run the following command:

```bash
./download_json.sh
```

You can move the script out of that folder afterwards. Then, if you want even more specs, follow [this link](https://drive.google.com/file/d/1PDc238fkooRJqSI-K5SkeSwkKYmC9Uk6/view) to generate data from Google's GitHub bigquery dataset. Requires additional setup.

2. Make sure you've modified the node packages by replacing the files in `node_modules/` with the corresponding modified versions in `modified node packages/`.

2. In `step 1/`, run the following command :

```bash
./generate_curl.sh
```

3. Use `curl_parsing.ipynb` to process the curl commands and remove blatantly correct or overly long ones. Return to step 2 and repeat until you have your desired distribution of curl commands. To stop generating commands for a specific method, you can edit `isEndpointValid` in `base_model_gen/step 1/node_modules/openapi-snippet/openapi-to-har.js` to change which methods are not skipped. 

4. Combine all the generated commands into a dataset and upload it to Azure ML as a dataset. Then use `base_model_gen/step 2/llama_test.ipynb` in azure ML with a powerful compute instance to schedule a job that runs `base_model_gen/step 2/rest_base_instruction_gen.py`.

5. Register the output of the job as a dataset in azureml. Then, use `base_model_gen/step 3/dataset_download.ipynb` (stile in Azure ML) to combine everything into one csv. Download that file.

6. Use `base_model_gen/step 3/instruction_parsing.ipynb` locally to process and tokenize the resulting dataset so everything is perfectly formatted for the model.
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

To use the API Pack, run the following command in `base_model_gen`:

```bash
./generate_curl.sh
```

# Scraping
follow [this link](https://drive.google.com/file/d/1PDc238fkooRJqSI-K5SkeSwkKYmC9Uk6/view) to generate data from Google's GitHub bigquery dataset. Requires additional setup.
// Load input data
function load_input(input_file){
    // if the input ends in .yaml, load it with js-yaml
    if (input_file.endsWith('.yaml')) {
        return yaml.load(fs.readFileSync(input_file, 'utf8'));
    }
    else {
        return require(input_file);
    }
}

// Save output as json file
function save_file(output_file, output) {
    const dir = path.dirname(output_file);

    // Check if the directory exists, if not, create it
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }

    // Now that the directory is ensured to exist, write the file
    fs.writeFile(output_file, output, (error) => {
        if (error) {
            console.error(error);
            throw error; // Throw error to handle it outside if necessary
        }
        console.log(`${output_file} was saved!`);
    });
}

// Generate snippets for each endpoint
function generate_api_calls(data, input_file){
    let calls = [];
    for(var path in data["paths"]){
        // console.log(path)
        for(var method in data["paths"][path]){
            try {
                results_snippets = OpenAPISnippet.getEndpointSnippets(data, path, method, ['shell_curl']);
                let api_calls = [];
                for (let snippet of results_snippets["snippets"]) {
                    api_calls.push(snippet.content);
                }

                calls.push(...api_calls);
            }
            catch (error) {
                continue;
            }
        }
    }
    // converting the JSON object to a string
    return calls;
}

// Req arguments
const OpenAPISnippet = require('openapi-snippet');
const yaml = require('js-yaml');
var fs = require('fs');
var path = require('path');
var arguments = process.argv;

// Directories
const INPUT_FILE =  arguments[2];
const OUTPUT_FILE = `./data/curl_commands.txt`;

// Call functions here
data = load_input(`./scraped_specs/${INPUT_FILE}.${arguments[3]}`);
// load text from curl_commands.txt
all_calls = fs.readFileSync(OUTPUT_FILE, 'utf8');
output = generate_api_calls(data, INPUT_FILE);
output = all_calls.split("\n").concat(output);
save_file(OUTPUT_FILE, output.join("\n"));
console.log("-----------------")
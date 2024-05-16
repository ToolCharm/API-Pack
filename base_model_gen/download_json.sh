#!/bin/bash

# Array containing all the new URLs
urls=(
    "https://api.apis.guru/v2/specs/amazonaws.com/AWSMigrationHub/2017-05-31/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/accessanalyzer/2019-11-01/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/acm/2015-12-08/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/acm-pca/2017-08-22/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/alexaforbusiness/2017-11-09/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/amp/2020-08-01/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/amplify/2017-07-25/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/amplifybackend/2020-08-11/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/apigateway/2015-07-09/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/apigatewaymanagementapi/2018-11-29/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/apigatewayv2/2018-11-29/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/appconfig/2019-10-09/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/appflow/2020-08-23/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/appintegrations/2020-07-29/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/application-autoscaling/2016-02-06/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/application-insights/2018-11-25/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/applicationcostprofiler/2020-09-10/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/appmesh/2019-01-25/openapi.json"
    "https://api.apis.guru/v2/specs/amazonaws.com/apprunner/2020-05-15/openapi.json"
    "https://api.apis.guru/v2/specs/apache.org/2.5.1/openapi.json"
    "https://api.apis.guru/v2/specs/api.ebay.com/sell-compliance/1.4.1/openapi.json"
    "https://api.apis.guru/v2/specs/apideck.com/accounting/9.3.0/openapi.json"
    "https://api.apis.guru/v2/specs/azure.com/EnterpriseKnowledgeGraph-EnterpriseKnowledgeGraphSwagger/2018-12-03/swagger.json"
    "https://api.apis.guru/v2/specs/azure.com/resourcegraph/2019-04-01/swagger.json"
)

# Loop through each URL and download the file with a custom name
for url in "${urls[@]}"; do
    # Extract the last three sections of the URL
    filename=$(echo "$url" | awk -F'/' '{print $(NF-2)"_"$(NF-1)"_"$NF}')
    # Download the file and save it with the custom name
    wget -O "$filename" "$url"
done

echo "All files have been downloaded."

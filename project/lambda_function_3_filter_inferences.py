import json

# Define the confidence threshold
THRESHOLD = 0.93

def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = json.loads(event["body"]['inferences'])  # Assuming inferences is a list of confidence scores
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(float(inference) > THRESHOLD for inference in inferences)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        # Continue with the workflow
        return {
            'statusCode': 200,
            'body': "THRESHOLD MET"
        }
    else:
        # Raise an error if no inferences meet the threshold
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

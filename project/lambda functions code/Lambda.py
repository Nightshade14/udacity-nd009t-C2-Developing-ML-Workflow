# data serialization - lambda 1
import json
import boto3
import base64
import traceback

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    try:
        key = event["s3_key"]
        bucket = event["s3_bucket"]
        
        # Download the data from s3 to /tmp/image.png
        s3.download_file(bucket, key, '/tmp/image.png')
        
        # We read the data from a file
        with open("/tmp/image.png", "rb") as f:
            image_data = base64.b64encode(f.read())
    
        # Pass the data back to the Step Function
        response = {
            "statusCode": 200,
            "body": 
                {
                    "image_data": image_data
                }
            
        }

        return response
        
    except Exception as e:
        return {
           "statusCode": 500,
           "body": {
               "error": str(e),
               "traceback": traceback.format_exc()
           }
        }



# classification - lambda 2
import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
import traceback

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-08-28-22-16-25-994"  # Replace with your SageMaker endpoint name

def lambda_handler(event, context):
    try:
        # Decode the image data
        image = base64.b64decode(event["body"]["image_data"])  # Decode the base64 image data
        print("successfully loaded the image")
        # Instantiate a Predictor
        predictor = sagemaker.Predictor(ENDPOINT)
        print("preidctor created")
        
        # For this model, the IdentitySerializer needs to be "image/png"
        predictor.serializer = IdentitySerializer("image/png")
        print("predictor serialized")
        
        # Make a prediction
        inferences = predictor.predict(image)
        print("inference complete")
        
        # We return the data back to the Step Function    
        inferences = inferences.decode('utf-8')  # Decode the prediction result to a string
        print("inference decoded as utf-8\nReady to return")
        
        return {
            "statusCode": 200,
            "body": {
                "inferences": str(inferences)
                }
        }
    except:
        return {
            "statusCode": 404,
            "body": {
                "error": str(traceback.extract_stack())
            }
        }




# filter inference - lambda 3
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

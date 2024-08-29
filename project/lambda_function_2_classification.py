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

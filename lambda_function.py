import json
import boto3
import os
import urllib.parse
from io import BytesIO
from PIL import Image

s3_client = boto3.client('s3')

# Fallback string matching your exact destination bucket name
DEST_BUCKET = os.environ.get('DEST_BUCKET', 'ayushi-images-destination')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    
    for record in event['Records']:
        source_bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        # Infinite loop protection guardrail
        if source_bucket == DEST_BUCKET:
            print(f"Skipping {key}: Prevented recursive execution cycle.")
            continue
            
        try:
            # 1. Stream object from Source S3 bucket into Lambda memory
            print(f"Downloading {key} from {source_bucket}...")
            response = s3_client.get_object(Bucket=source_bucket, Key=key)
            image_content = response['Body'].read()
            
            # 2. Process image optimizations using Pillow
            with Image.open(BytesIO(image_content)) as img:
                # Normalize color space data profiles (RGBA/P to standard web RGB)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Perform structural aspect-ratio thumbnail calculation
                img.thumbnail((150, 150))
                
                # 3. Serialize optimized image structure to memory byte buffer
                buffer = BytesIO()
                img.save(buffer, 'JPEG', optimize=True, quality=85)
                buffer.seek(0)
                
                # Format clean output key structure
                clean_filename = key.rsplit('.', 1)[0]
                new_key = f"thumbnails/thumbnail-{clean_filename}.jpg"
                
                # 4. Upload payload back to Destination S3 Bucket
                print(f"Uploading {new_key} to {DEST_BUCKET}...")
                s3_client.put_object(
                    Bucket=DEST_BUCKET,
                    Key=new_key,
                    Body=buffer,
                    ContentType='image/jpeg'
                )
                
            print(f"Successfully processed {key} and saved to {DEST_BUCKET}")
            
        except Exception as e:
            print(f"Error executing optimization on key {key}: {str(e)}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Image execution pipeline finalized.')
    }

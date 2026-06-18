# AWS Image Processor 

A serverless image processing pipeline built on AWS.

## Architecture
- **S3 Source Bucket** → stores original images
- **AWS Lambda** → auto-triggered, processes images
- **S3 Destination Bucket** → stores processed thumbnails

## Features
- Auto-triggered on S3 upload
- Image compression & optimization
- Thumbnail generation
- Built with Python & Pillow

## Tech Stack
- AWS Lambda (Python 3.12)
- Amazon S3
- IAM Roles & Policies
- CloudWatch Logs

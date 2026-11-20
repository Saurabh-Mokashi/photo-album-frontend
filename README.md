# Photo album frontend

Cloud Computing and Big Data Systems, Assignment 3.

A static photo album with natural-language search, image results, JPEG/PNG upload, and optional comma-separated custom labels. Requests use the API Gateway-generated JavaScript SDK in `sdk/`.

## Working deployment

- Website: http://cc-s3-b1-36234.s3-website-us-east-1.amazonaws.com
- Frontend bucket: `cc-s3-b1-36234`
- API base: https://s0khdyagpg.execute-api.us-east-1.amazonaws.com/test
- Region: `us-east-1`

Enter the photo-album API key in the page. It stays in the current page's memory and is not stored by this application. Do not commit the key or AWS credentials. The photo bucket remains private; search results use temporary presigned image URLs.

## Build locally

Requires Python 3.12+ and Node.js 22 in CodeBuild. Local equivalent commands:

```bash
node --check app.js
python3 scripts/build.py
```

The build checks JavaScript syntax and verifies every script/stylesheet referenced by index.html exists. It copies only website assets into `dist/`, with index.html at its root. `dist/` is generated and ignored by Git. The build does not call AWS or deploy anything locally.

## Frontend CodePipeline (P2)

Create a pipeline in us-east-1 with queued execution and these actions:

1. Source: GitHub App connection with the AWS Connector actually installed for this repository, main branch, push trigger for main, default ZIP source artifact.
2. Build: CodeBuild project reading root `buildspec.yml`, using an AWS managed image supporting Python 3.12 and Node.js 22. Choose the source artifact as input and produce BuildArtifact.
3. Deploy: Amazon S3, bucket `cc-s3-b1-36234`, input BuildArtifact, with Extract file before deploy enabled. Leave deployment path blank to place index.html at the bucket root. Do not select the private photo bucket or the CloudFormation demonstration bucket.

CodeBuild builds the static files; the S3 deploy action uploads them. Unlike the backend, this buildspec does not deploy in post_build. Configure the pipeline service role to use its connection, read pipeline artifacts and put website objects in the destination bucket. The CodeBuild role needs build logs and artifact access. No Lambda permissions are needed for this frontend build role.

To prove automatic deployment, change visible page text in index.html, commit and push main, and verify a Commit-triggered successful pipeline execution plus the updated page after a hard refresh. Save the commit ID and success screenshot. Then smoke-test search, upload with a unique custom label, and search for that label after indexing.

## Generated SDK binary compatibility

The generated SDK's apiGatewayClient.js and utils.js have small binary compatibility fixes: Blob/ArrayBuffer bodies must not be discarded as empty objects or copied using a constructor without new. Keep these fixes if regenerating the SDK. The deployed browser upload and custom-label search were verified before pipeline setup.

## Manual hosting and cleanup

S3 static website hosting uses index.html. The frontend bucket policy grants public GetObject access; private photo storage is separate. A manual upload copies only the contents of dist/ to the frontend bucket. A pipeline S3 deploy overwrites included files but does not remove old objects absent from a newer artifact. Stop/delete assignment pipelines and unused resources after grading according to your retention needs; avoid deleting shared working resources while collecting evidence.

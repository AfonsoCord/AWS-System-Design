# Project: Banking Loan Management System

A full stack banking application for managing loan requests, with face recognition login and an automated credit decision workflow.

## Workflow
1. A customer logs in through face recognition, powered by AWS Rekognition, and submits a loan request through the React frontend.
2. The Django REST backend authenticates requests with JWT and stores loan and scheduling data in a MySQL database.
3. An AWS Step Functions workflow triggers Lambda functions that calculate a credit score and determine the loan decision.
4. A bank employee reviews and finalizes the decision through a separate React frontend built for internal staff.
5. The backend and frontends are deployed on AWS Elastic Beanstalk.

## Technologies
Django REST Framework, React, MySQL, AWS Rekognition, AWS Step Functions, AWS Lambda, AWS Elastic Beanstalk, JWT.

## Contents
* `backend/` Django REST API for authentication, loan requests, and scheduling
* `frontend/` React app for customers
* `frontend_bank/` React app for bank employees
* `workflow/` AWS Lambda functions for credit score calculation and loan decisions

## Setup
The backend expects the following environment variables, set through `.env.local`, which is not committed:
* `DJANGO_SECRET_KEY`
* `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
* `S3_BUCKET_NAME`, `STATE_MACHINE_ARN`

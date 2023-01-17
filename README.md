# Starter Kit V1 for Django SaaS projects
The Starter Kit is designed to provide a solid foundation for SaaS projects based on the Django framework, with a focus on scalability, security, and maintainability, so you can focus on building your product's features.

## To Do
- Add logger to main project
- Billing page
- Move Users page to Settings area

## Start from Scratch!
- Create AWS Account
    - Set a secret in "AWS Secrets Manager"
        - Database username (DATABASE_USER)
        - Database password (DATABASE_PASSWORD)
        - Secret key (SECRET_KEY)
        - 

## Includes
- Auth0 for user management
- Profile page
    - Update name
    - Update email
- Password page
    - Update password
- Billing page
    - Update primary credit card
    - Display past invoices
- Users page
    - Add & remove additional users

## Prerequisites
- Auth0 account
    - 2 tenants
        - Development
        - Production
- Stripe account
    - Test API keys
    - Development API keys
- DigitalOcean account
    - Read/Write API key for Github Actions
- Docker account with Docker Desktop installed locally
- Terraform Cloud Workspace

## Initial setup
- Fork/create new repository from template
- Setup a new python virtual environment
    - Run 'pip install -r requirements.txt'
- Run 'npm install'

## Environment Variables in Production
- Database (NAME, USER, PASSWORD, HOST, PORT)
    - DATABASE_NAME
    - DATABASE_USER
    - DATABASE_PASSWORD
    - DATABASE_HOST
    - DATABASE_PORT
- Auth0 Credentials (CLIENT_ID, CLIENT_SECRET, DOMAIN)
    - AUTH0_CLIENT_ID
    - AUTH0_CLIENT_SECRET
    - AUTH0_DOMAIN
- AWS Credentials (Ensure IAM permissions are set, minimum permissions required is SES)
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
- Domain names for Allowed Host (ASSIGNED_DOMAIN_NAME, APPLICATION_DOMAIN_NAME)
    - ASSIGNED_DOMAIN_NAME is the domain name created by the PaaS, which is automatically assigned to the container
    - APPLICATION_DOMAIN_NAME is the domain name for the application that requires DNS changes
- Stripe
    - STRIPE_API_KEY
# Boilerplate starting point for Django projects

## To Do
- Add logger to main project

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
# SplitIn Backend

## Setup environment variables  
`cp settings.py.example settings.py`

## Migrate database
1. `flask --app manage db init`  
2. `flask --app manage db migrate`  
3. `flask --app manage db upgrade`  

## Seed database  
#todo

## Run in development
`flask --app app --debug run`
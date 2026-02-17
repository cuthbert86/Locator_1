Staff App
   ↓
POST /login  → FastAPI verifies credentials
   ↓
JWT Token returned
   ↓
Staff includes token in future requests
   ↓
Protected endpoints verify token
   ↓
Database stores submissions

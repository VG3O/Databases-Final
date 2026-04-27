# ChatApp

This application is designed to provide multiple clients with a seamless chatting experience with the following features:
- Account creation, management, personalization
- Chatting within multiple channels with different users present
- Automatic message reconciliation and updating when edits are present

## Development Stack
The development stack for my app will utilize the following:
- **FastAPI** for a well-structued and documented backend system
- **Vite/React** for a clean front-end interface
- **PostgreSQL** for account management and relational tables
- **MongoDB** for message handling and filtering
- **Redis** for live session handling and pub/sub for every connected client

### Current Progress
#### (4/6/2026)
- Docker containerization setup completed
- Postgres and Mongo are running and can be interacted with from the backend API
- A basic web GUI for interacting with users and messages
#### (4/26/2026), yes i know
- Pub-sub works and clients can now see messages they send
- First starting UI pass

#### (4/27/2026)
- Pretty much finished for the final
- Login, create accounts, error handling
- Channels, loading message history from mongo and saving
- Showing username and send date
- Known issue where logging in on another client with the same username as another active session will NOT boot the other person off the session 

## Runtime Instructions
Pull the repository and and run the following command within the root of the repository:
```bash
  docker compose up -d
```
**NOTICE:** Make sure you have [Docker](https://www.docker.com/products/docker-desktop/) installed on your sysytem, since this project only runs locally!

Adminer Interface Credentials:
- Server: postgres
- Username: postgres
- Password: postgres
- Database: chatdb

Mongo Express Credentials:
- Username: admin
- password: admin
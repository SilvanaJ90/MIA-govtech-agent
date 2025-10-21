# Chat Message Processing API – Backend Developer (Python)
---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Functional Requirements](#functional-requirements)  
3. [API Endpoints](#api-endpoints)  
4. [Example Requests](#example-requests)  
5. [Error Handling](#error-handling)  
6. [Project Structure](#project-structure)  
7. [How to Start It](#how-to-start-it)  
8. [Run Tests](#run-tests)  
9. [Technology Stack](#technology-stack)  
10. [Authors](#authors)  

---


## Project Overview
This project is a RESTful API built with Python and Flask, designed to process chat messages.
It allows receiving, validating, processing, storing, and retrieving messages efficiently.

The project evaluates backend development skills in:

- Designing and implementing clean, maintainable APIs

- Error handling and input validation

- Unit and integration testing

- Code and API documentation

---

### General Objective
Build a simple and maintainable message-processing API that follows backend development best practices.

### Specific Objectives
- Implement a **POST endpoint** `/api/messages` to receive and validate messages.  
- Implement a **GET endpoint** `/api/messages/{session_id}` to retrieve messages by session, with optional filters.  
- Apply a processing pipeline for validation and metadata creation.  
- Separate concerns into **controllers, services, and repositories**.  
- Include **unit and integration tests** using Pytest.  
- Provide **comprehensive documentation** for the API.
---



## Functional Requirements

**POST /api/messages**

- Accepts messages in JSON format

- Validates required fields (session_id, content, sender)

- Filters prohibited words

- Processes messages by adding metadata (word_count, character_count, processed_at)

- Stores the message in the database

- Returns response with appropriate HTTP status code


**GET /api/messages/{session_id}** 

- Returns all messages for a specific session

- Supports pagination with limit and offset query parameters

- Allows filtering by sender (user or system)

---

### API Endpoints
**http://127.0.0.1:5000/apidocs/**

<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/api.png">
</p>

**POST /api/messages**

Creates a new chat message in the system

**Request Payload**

<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/payload.png">
</p>

**Success Response**
<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/response%20post.png">
</p>

**Error Response**



<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/error-post.png">
</p>

**GET /api/messages**
Retrieves all messages for a given session.
<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/get.png">
</p>


**Success Response**
<p align="center">
  <img width="800" height="800" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/response-get.png">
</p>




---
## Error Handling
The API handles errors for:

- Missing required fields

- Invalid data format

- Inappropriate content

- Internal server errors

All errors return a JSON response with status: error and detailed information.

---

##  Project Structure

<p align="center">
  <img width="600" height="600" src="https://github.com/SilvanaJ90/Images/blob/main/ApiNequiBot/infraestructure.png">
</p>


---

## Development Phases

| Phase | Description |
|-------|-------------|
| **1. API Design** | Define RESTful endpoints and message data schema. |
| **2. Validation & Processing** | Validate JSON input, filter forbidden words, and generate metadata (word count, length, timestamp). |
| **3. Database Layer** | Implement SQLite database and CRUD operations for message storage. |
| **4. Error Handling** | Create custom error responses with appropriate HTTP status codes. |
| **5. Testing** | Implement unit and integration tests with Pytest (minimum 80% coverage). |
| **6. Documentation** | Document API endpoints in README and/or Swagger UI (if using FastAPI). |



---



## How to Start It

| Step                         | Command | Description |
|------------------------------|---------|-------------|
| Clone the project            | `git clone https://github.com/SilvanaJ90/nequibot_assessment-backend.git` | Clone the repository |
| Move to project folder       | `cd backend-developer-assessment-python` | Navigate into project directory |
| Create virtual environment   | `python -m venv .venv` | Create isolated Python environment |
| Activate on Windows          | `.\.venv\Scripts\Activate.ps1` | Activate environment on Windows |
| Activate on Git Bash         | `source .venv\Scripts\activate` | Activate environment on Git Bash |
| Activate on macOS/Linux      | `source .venv/bin/activate` | Activate environment on macOS/Linux |
| Install dependencies         | `pip install -r requirements.txt` | Install all required packages |
| Run development server (Flask Api) | `python run.py` | Start the API locally |

## Run Tests
This project includes unit and integration tests using Pytest to ensure the API works as expected. Tests cover message posting, validation, error handling, and message retrieval.

Test Coverage

The tests aim to cover at least 80% of the code, including:

**POST /api/messages:**

- Minimal valid message

- Message with non-existent sender

- Message containing banned words

**GET /api/messages/{session_id}:**

- Retrieve messages from a valid session

- Invalid session retrieval

| Test Function                            | Purpose                                                               | Expected Result                                                            |
| ---------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `test_post_message_minimal`              | Test sending a minimal valid message                                  | 201 Created, success status, content and sender match                      |
| `test_post_message_sender_not_found`     | Test sending a message with invalid sender                            | 404 Not Found, error code `NOT_FOUND`                                      |
| `test_post_message_banned_word`          | Test message containing banned words                                  | 403 Forbidden, error code `FORBIDDEN`                                      |
| `test_post_message_legacy_sender_user`   | Test sending a message using legacy `sender` field                    | 201 Created, success status                                                |
| `test_post_message_invalid_json`         | Test sending invalid JSON                                             | 400 Bad Request, error code `INVALID_REQUEST`                              |
| `test_post_message_invalid_payload`      | Test sending payload with invalid types                               | 400 Bad Request, error indicating field validation error                   |
| `test_post_message_service_exception`    | Test handling service layer exceptions during message creation        | 500 Internal Server Error, error code `SERVER_ERROR`                       |
| `test_get_messages`                      | Test retrieving messages for a valid session                          | 200 OK, success status, message content matches                            |
| `test_get_messages_invalid_session`      | Test retrieving messages for a non-existent session                   | 404 Not Found, error code `NOT_FOUND`                                      |
| `test_get_messages_invalid_limit_offset` | Test retrieving messages with invalid `limit` and `offset` parameters | 400 Bad Request, error code `INVALID_REQUEST`                              |
| `test_get_messages_service_value_error`  | Test handling service layer ValueError when listing messages          | 404 Not Found, error code `NOT_FOUND`                                      |
| `test_get_messages_service_exception`    | Test handling service layer exceptions during message retrieval       | 500 Internal Server Error, error code `SERVER_ERROR`                       |
| `test_message_in_valid_and_invalid`      | Test validation for `MessageIn` schema                                | Valid input passes, invalid sender_type or empty content raises ValueError |
| `test_message_out_serialization`         | Test serialization of `MessageOut` schema                             | Correct dictionary output, fields match                                    |
| `test_sender_creation`                   | Test creation of a sender and password verification                   | Sender email starts with `test_`, password verification passes             |
| `test_sender_password_update`            | Test updating a sender's password                                     | Password updated successfully, verification passes                         |
| `test_session_creation`                  | Test creation of a session for a sender                               | Session's `user_id` matches sender ID, session has `session_id` attribute  |
| `test_404_handler`                       | Test Flask 404 error handler                                          | 404 Not Found, error code `NOT_FOUND`                                      |
| `test_400_handler`                       | Test Flask 400 error handler                                          | 400 Bad Request, error code `BAD_REQUEST`                                  |
| `test_500_handler`                       | Test Flask 500 error handler                                          | 500 Internal Server Error, error code `SERVER_ERROR`                       |


### How to Run Tests

1 **Export PYTHONPATH**
- Before running tests, export the project root so Python can locate modules:
```
export PYTHONPATH=.
```

2 **Run Pytest**
- Run the tests with verbose output:
```
pytest -v tests/
```

3 **Expected Output:**

```
collected 20 items

tests/test_errors.py::test_404_handler PASSED                                                                                                                                 [  5%]
tests/test_errors.py::test_400_handler PASSED                                                                                                                                 [ 10%]
tests/test_errors.py::test_500_handler PASSED                                                                                                                                 [ 15%]
tests/test_messages.py::test_post_message_minimal PASSED                                                                                                                      [ 20%]
tests/test_messages.py::test_post_message_sender_not_found PASSED                                                                                                             [ 25%]
tests/test_messages.py::test_post_message_banned_word PASSED                                                                                                                  [ 30%]
tests/test_messages.py::test_post_message_legacy_sender_user PASSED                                                                                                           [ 35%]
tests/test_messages.py::test_post_message_invalid_json PASSED                                                                                                                 [ 40%]
tests/test_messages.py::test_post_message_invalid_payload PASSED                                                                                                              [ 45%]
tests/test_messages.py::test_post_message_service_exception PASSED                                                                                                            [ 50%]
tests/test_messages.py::test_get_messages PASSED                                                                                                                              [ 55%]
tests/test_messages.py::test_get_messages_invalid_session PASSED                                                                                                              [ 60%]
tests/test_messages.py::test_get_messages_invalid_limit_offset PASSED                                                                                                         [ 65%]
tests/test_messages.py::test_get_messages_service_value_error PASSED                                                                                                          [ 70%]
tests/test_messages.py::test_get_messages_service_exception PASSED                                                                                                            [ 75%]
tests/test_messages.py::test_message_in_valid_and_invalid PASSED                                                                                                              [ 80%]
tests/test_messages.py::test_message_out_serialization PASSED                                                                                                                 [ 85%]
tests/test_senders.py::test_sender_creation PASSED                                                                                                                            [ 90%]
tests/test_senders.py::test_sender_password_update PASSED                                                                                                                     [ 95%]
tests/test_sessions.py::test_session_creation PASSED                                                                                                                          [100%]

================================================================================ 20 passed in 5.74s ================================================================================ 

```

4 **Coverage Repor**

```
  pytest --cov=app tests/
```
Coverage should be ≥ 80%.

```
collected 20 items

tests\test_errors.py ...                                                                                                                                                      [ 15%]
tests\test_messages.py ..............                                                                                                                                         [ 85%]
tests\test_senders.py ..                                                                                                                                                      [ 95%]
tests\test_sessions.py .                                                                                                                                                      [100%]

================================================================================== tests coverage ================================================================================== 
_________________________________________________________________ coverage: platform win32, python 3.13.9-final-0 __________________________________________________________________ 

Name                                         Stmts   Miss  Cover
----------------------------------------------------------------
app\__init__.py                                 15      0   100%
app\api\__init__.py                              3      0   100%
app\api\controllers\messages.py                 76      7    91%
app\api\errors.py                               11      0   100%
app\api\repositories\message_repository.py      15      1    93%
app\api\schemas.py                              29      1    97%
app\api\services\message_service.py             32      3    91%
app\api\utils\text_processing.py                17      0   100%
app\config.py                                    6      0   100%
app\models\banned_word.py                        5      0   100%
app\models\base_model.py                        30      9    70%
app\models\message.py                           19      0   100%
app\models\sender.py                            25      2    92%
app\models\session.py                            9      0   100%
app\models\storage.py                           32      3    91%
----------------------------------------------------------------
TOTAL                                          324     26    92%
```
---



## Technology Stack

| Technology | Badge |
|------------|-------|
| <p align="left"><a href="https://www.python.org" target="_blank"><img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue"/></a></p> | **Python 3.10+**   |
| <p align="left"><a href="https://flask.palletsprojects.com/" target="_blank"><img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/></a></p> | **Flask** for the API   |
| <p align="left"><a href="https://www.sqlite.org/" target="_blank"><img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/></a></p> | **SQLite** as the database   |
| <p align="left"><a href="https://www.sqlalchemy.org/" target="_blank"><img src="https://img.shields.io/badge/SQLAlchemy-FF0000?style=for-the-badge&logo=sqlalchemy&logoColor=white"/></a></p> | **SQLAlchemy** as the ORM   |
| <p align="left"><a href="https://docs.pytest.org/" target="_blank"><img src="https://img.shields.io/badge/Pytest-5A5A5A?style=for-the-badge&logo=pytest&logoColor=orange"/></a></p> | **Pytest** for unit and integration tests   |

---

## Authors
[![contributors](https://contrib.rocks/image?repo=SilvanaJ90/nequibot_assessment-backend)](https://github.com/SilvanaJ90/nequibot_assessment-backend/graphs/contributors)  
Silvana Jaramillo

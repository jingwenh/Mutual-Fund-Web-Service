# Mutual-Fund-Web-Service
## Architechture Overview
![architecture](https://github.com/jingwenh/Mutual-Fund-Web-Service/blob/master/Mutual%20Fund.png?raw=true)
The whole system is built upon a **microservice architecture**, and can be mainly five parts:  
* Login / logout service: user can send username and password to login service, if the credentials are correct, an encrypted token will be assigned to the in the cookie. Requesting the logout service can invalidate current token.
* Access control service: authenticates user's token and response with username if succeed
* Application services: provides specific service after successful authentication by the access control service
* Database: where data of the whole system is held
* API Gateway: wrap-up the services and transfer requests and responses

## Technology Used
* Python
* AWS Lambda
* AWS API Gateway
* MySQL + AWS RDS

## Trade-offs in System Design
### Monolith system vs. Microservices
#### Design Decision
In our design, we use microservice architectures for following reasons:  
* Dividing system into smaller parts are easier to understand and divide work
* Easier to separate back-end from front-end
* Easier to scale
* A fault in one system won't effect the whole system
#### Downside & Solution
One problem in microservice architecture is that communication between services is slower than a monolith system. But there is not a strict requirement on the response time of the system and therefore we didn't find any trouble in this aspect.

### Server vs. Serverless


### NoSQL vs. RDBMS

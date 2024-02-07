Manage Blue / Green, Canary Deployment and Rollback [CN]
==============================================================================
AWS Chalice 框架不支持 blue green testing. 不过你可以用两个 environment, 例如 prod1, prod2 来分别部署一套 API Server, 然后用 load balancer 来做 blue green 或 canary deployment.

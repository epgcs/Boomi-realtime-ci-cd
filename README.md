# boomi-ci-cd-robust-automation
1. **Automatic package version  <>  Instead of manually editing:**
2. **Deployment verification  <>  After deployment, GitHub should check Boomi and confirm:**

Boomi CI/CD approach suggested structure :
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                       **WORKFLOW**
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
boomi-ci-cd-robust
package.py
    │
    ├── package_id = 04a3...
    └── package_version = 8.1
             │
             ▼
       GitHub Output
             │
             ▼
       deploy.py
             │
             ├── Deploy
             │
             ├── Get deploymentId
             │
             ▼
   GET /DeployedPackage/{deploymentId}
             │
             ├── Package ID ✓
             ├── Version ✓
             ├── Environment ✓
             ├── Process ✓
             └── active = true ✓
             │
             ▼
          SUCCESS

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                      **ARCHITECTURE**
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    GitHub Repository
                           │
                           │ push
                           ▼
                 GitHub Actions Workflow
                  boomi-deploy.yml
                           │
              ┌────────────┴────────────┐
              │                         │
         Validate                     Package
        validate.py                   package.py
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                    Boomi API
                           │
                           ▼
                Packaged Component
                           │
                           ▼
                    Deploy Package
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                  BETA          PROD

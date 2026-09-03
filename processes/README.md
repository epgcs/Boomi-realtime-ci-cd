
What about the actual Boomi process?

This is important.

You shouldn't simply copy/paste the Boomi process XML/JSON manually and assume GitHub can deploy it.

Your CI/CD pipeline needs to know:

Boomi Process
       ↓
Package
       ↓
Package/component version
       ↓
GitHub
       ↓
GitHub Actions
       ↓
Boomi API
       ↓
Beta
       ↓
Prod

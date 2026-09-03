What should config/beta.json contain?
Think of this file as environment configuration, not secrets.

{
  "environment": "beta",
  "environment_id": "YOUR_BETA_ENVIRONMENT_ID",
  "atom_id": "YOUR_BETA_ATOM_ID",
  "processes": [
    {
      "name": "MyProcess",
      "process_id": "YOUR_BOOMI_PROCESS_ID"
    }
  ]
}

And prod.json:

{
  "environment": "prod",
  "environment_id": "YOUR_PROD_ENVIRONMENT_ID",
  "atom_id": "YOUR_PROD_ATOM_ID",
  "processes": [
    {
      "name": "MyProcess",
      "process_id": "YOUR_BOOMI_PROCESS_ID"
    }
  ]
}

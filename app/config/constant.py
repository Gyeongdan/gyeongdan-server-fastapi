import os

service_name = "translator"  # pylint: disable=invalid-name
environment = os.getenv("ENVIRONMENT", "dev")

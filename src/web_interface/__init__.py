"""
Web Interface Domain
===================
Frontend presentation and web interface functionality.

Clean Architecture Layers:
- Domain: UI domain logic and models
- Application: UI use cases and services  
- Infrastructure: Web server, routing, middleware
- Presentation: Templates, static files, components
"""

from .presentation import *

__version__ = "1.0.0"
__domain__ = "web_interface"
